from pymongo import MongoClient
import os
from dotenv import load_dotenv
import datetime
from pydantic import BaseModel,ValidationError, field_validator,Field,validator, EmailStr
from typing import Literal, Optional
from tags_algorithm import tagging_algorithm
from json import dumps
from pymongo.errors import OperationFailure
import re
from mysql.connector import connect, Error, IntegrityError
from bson import ObjectId
from disposable_email_domains import blocklist
from scripts.company_verifier import check_company_existence
import asyncio
from json import JSONEncoder
from json import loads
load_dotenv()

uri = os.getenv("MONGO_URL")
client = MongoClient(uri)
#DATABASE = os.getenv("DB_NAME")
#db = client[DATABASE]
#collection = db["threads"]


class InsertData(BaseModel):
    username:Optional[str] = Field(None,max_length=14)
    email:Optional[EmailStr] = None
    thread_text:Optional[str] = Field(None,max_length=6000)
    category:Optional[Literal["jobb", "lön","arbetsmiljö","arbetsgivare","kultur"]] = None
    company_profile:Optional[str] = None
    star_ratings:Optional[Literal[1,2,3,4,5]] = None

    @field_validator("thread_text")
    @classmethod
    def validate_thread_text(cls,value):
        if value is not None:
            if len(value) < 500:
                raise ValueError("Thread text is too short")
        return value
    
    @field_validator("company_profile")
    @classmethod
    def validate_compamy_name(cls,value):
        if value is None:
            raise ValueError("Company name can not be 'None")
        
        value_array  = [i for i in value.split()]
        if len(value_array)>1:
            raise ValueError(f"Lenght of array (company name):{value} exceeds 1, use '-' for each word in a company name")
        
        value_str = str(value_array)
        value_str = value.replace("'","")
        value_str = value.replace("[","")
        value_str = value.replace("]","")

        if "-" not in value_str:
            raise ValueError("Company name name must contain '-'")
        
        if bool(re.search(r"\s",value_str)):
            raise ValueError("Company name name can not contain spaces")
        return value
    
    @field_validator("email")
    @classmethod
    def validate_email(cls,value):
        if value in blocklist:
            raise ValueError("Email is part of the blacklisted email providers")
        return value

import bcrypt
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'),bcrypt.gensalt())

def check_password(hashed_password,plain_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

import hashlib
import base64
def check_email(email,hashed_email):
    sha256_hash = hashlib.sha256(email.encode('utf-8')).digest()
    expected_hash = base64.b64encode(sha256_hash).decode('utf-8')
    return hashed_email==expected_hash
def hash_email(email):
    sha256_hash = hashlib.sha256(email.encode('utf-8')).digest()
    hashed_email = base64.b64encode(sha256_hash).decode('utf-8')
    return hashed_email


class MySQLHandler:
    def __init__(self):
        self.database = connect(
            host = os.getenv("HOST"),
            port = os.getenv("PORT"),
            user = os.getenv("USER"),
            password = os.getenv("PASSWORD"),
            database = os.getenv("DATABASE_NAME")
                    )
    

    def create_table_query(self):
        query = """
                CREATE TABLE users(
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE,
                email VARCHAR(255) UNIQUE,
                password VARCHAR(255),
                acc_creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                rykte INT DEFAULT 0,
                verified BOOLEAN DEFAULT FALSE)
                """
        try:
            db_cursor = self.database.cursor()
            db_cursor.execute(query)
            db_cursor.close()
        except Error as e:
            return {f"Something went wrong: {e}"}
        return {"Succesfully created table"}
    
    

    def registerUser(self,username,password,email=None):
        hashed_email = hash_email(email=email)
        hashed_password = hash_password(password=password)
        if email:
            query = "INSERT INTO users(username,email,password,verified) VALUES (%s, %s, %s, %s)"
            values = (username,hashed_email,hashed_password,True)
        else:
            query = "INSERT INTO users(username,password,verified) VALUES (%s, %s)"
            values = (username,hashed_password,False)
        
        try:
            db_cursor = self.database.cursor()
            db_cursor.execute(query,values)
            self.database.commit()
            db_cursor.close()
        except IntegrityError as e:
            return {f"Username: '{username}' or '{email}' already registered":str(e)}
        except Error as e:
            return {f"Something went wrong: {e.msg}"}
        return {"Succesfully inserted data"}

        

    def authenticate(self,password,username=None,email=None):
        if email and username:
            raise ValueError("Must use username or email, can not use both")  
        
        elif username:
            query = f"SELECT password FROM users WHERE username = %s"
            param = (username,)
        elif email:
            hashed_email = hash_email(email=email)
            query = f"SELECT password FROM users WHERE email=%s"
            param = (hashed_email,)
        else:
            raise ValueError("No username or email was selected")
        
        try:
            db_cursor = self.database.cursor()
            db_cursor.execute(query,param)
            result = db_cursor.fetchone()
            db_cursor.close()

            if result is None:
                return {"Authentication failed":"User not found"}
            stored_password = result[0]
            if check_password(hashed_password=stored_password,plain_password=password):
                return {"Authentication succesfull":True}
            else:
                return {"Authentication failed":"Incorrect password"}
        except Error as e:
            return {"Something went wrong":str(e)}
        

class MongoDatabaseHandler:
    def __init__(self):
        pass

    #TODO We need to connect this with a SQL database which contains all of the user info such as username, email etc
    #TODO Maybe we can't store user threads in the company forum database, we'll need to store user threads in their own database..., but each thread needs to be tagged with which forum it was posted in

    @classmethod
    def threadRelationship(cls,thread):
        THREADS_RELATIONS_DB = client["threads-relations"]
        relations_collection = THREADS_RELATIONS_DB.relations

        data_payload = {"thread_id":thread["_id"],
                        "username":thread["username"],
                        "company_name":thread["company_name"] }
        
        try:
            relations_collection.insert_one(data_payload)
            return {"message":"Thread relationship succesfully created"}
        except OperationFailure as e:
            return {"error":f"Something went wrong: {e}"}
        
    @classmethod
    def commentsRelationship(cls, commenter, thread_id):
        COMMENTS_RELATIONS_DB = client["comments-relations"]
        relations_collection = COMMENTS_RELATIONS_DB.relations
        
        # Fetch the thread title from the main database
        DATABASE = "foretagsforum"
        db = client[DATABASE]
        companies_collection = db.companies
        
        try:
            # Find the thread and get its title
            thread = companies_collection.find_one(
                {"threads._id": ObjectId(thread_id)},
                {"threads.$": 1}
            )
            
            if not thread or not thread.get('threads'):
                return {"error": "Thread not found"}
            
            thread_title = thread['threads'][0].get('title_text', 'Untitled')
            
            data_payload = {
                "thread_id": thread_id,
                "thread_title": thread_title,
                "commenter": commenter
            }
            
            result = relations_collection.insert_one(data_payload)
            if result.inserted_id:
                return {"message": "Comment relationship successfully inserted", "id": str(result.inserted_id)}
            else:
                return {"error": "Failed to insert comment relationship"}
        except OperationFailure as e:
            return {"error": f"OperationFailure: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
        

    def createCompanyProfile(self,org_number:str):
        DATABASE = os.getenv("DB_NAME")
        db = client[DATABASE]
        collection = db.companies
        company_name = asyncio.run(check_company_existence(org_number))
        if company_name:
            data_payload = {
                "company_name":company_name,
                "org_number":org_number,
                "company_info":[],
                "threads": [],
            
            }
        else:
            return {"error":"company doesn't exist"}  
        try:
            if collection.find_one({"company_name":company_name}):
                return {"Message":"Company profile already exsists"}
            
            collection.insert_one(data_payload)
            return {"Message":"Succesfully inserted data"}
        
        except OperationFailure as e:
            return {"error":f"Something went wrong {e}"}
        
        

    #TODO add the following: "upvotes":int() and "downvotes":int()
    def insertDataThreads(self, title_text,username,thread_text,category,company_profile):
        tags:list = tagging_algorithm(thread_text).generate_tags(5)
        data_payload = {
            "_id":ObjectId(),
            "title_text":title_text,
            "username":username,
            "thread_text":thread_text,
            "tags":tags,
            "timestamp":datetime.datetime.now(tz=datetime.timezone.utc),
            "category":category,
            "company_name":company_profile,
            "comments":{}
        }
        DATABASE = os.getenv("DB_NAME")
        db = client[DATABASE]
        companies_collection = db.companies
        

        try:
            result = companies_collection.update_one(
                {"company_name":company_profile},
                {"$push":{"threads":data_payload}}
            )
            
            if result.modified_count > 0:
                inserted_thread = companies_collection.find_one(
                    {"company_name":company_profile},
                    {"threads": {"$slice":-1}}
                )["threads"][-1]

                MongoDatabaseHandler.threadRelationship(inserted_thread)
                response = dumps("Data succesfully inserted into the company profile")
            else:
                response = dumps("No company profile found to insert the data")
            return response

        except OperationFailure as e:
            return {f"Something went wrong:\n{e}"}

    #
    #TODO We need to somehow connect a specific thread with the correct comments, best way of doing this could be to get the objectId for a thread document
    def insertDataComments(self, company_profile, thread_id, commenter, comment_text):
        DATABASE = "foretagsforum"
        db = client[DATABASE]
        collection = db.companies

        try:
            company_doc = collection.find_one({"company_name": company_profile})
            if not company_doc:
                return {"error": "Company not found"}

            thread_id_obj = ObjectId(thread_id)

            # First, ensure 'comments' is an array
            collection.update_one(
                {"company_name": company_profile, "threads._id": thread_id_obj},
                {"$set": {"threads.$.comments": []}}
            )

            # Now, push the new comment
            result = collection.update_one(
                {"company_name": company_profile, "threads._id": thread_id_obj},
                {"$push": {"threads.$.comments": {"commenter": commenter, "comment_text": comment_text}}}
            )

            if result.matched_count == 0:
                return {"error": "Thread not found in company document"}

            # Call commentsRelationship class method
            relationship_result = MongoDatabaseHandler.commentsRelationship(commenter=commenter, thread_id=thread_id)
            
            if "error" in relationship_result:
                return {"warning": "Comment inserted, but relationship creation failed", "detail": relationship_result["error"]}

            return {
                "success": True, 
                "matched_count": result.matched_count, 
                "modified_count": result.modified_count,
                "relationship_created": relationship_result["message"]
            }

        except OperationFailure as e:
            return {"error": f"OperationFailure: {str(e)}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}
    
    def fetchUserThreads(self,username,items:int=1): 
        DATABASE = "threads-relations"
        db = client[DATABASE]
        thread = db.relations
        try:    
            user_threads = thread.find({"username":username}).limit(items)
            threads_list = list(user_threads)
            return threads_list
        
        except OperationFailure as e:
            return {"Something went wrong":str(e)}
        
    #---------------------Under construction---------------------
    def fetchUserComments(self,username,items=10,fetchComment = None):  #fetchComment takes the thread id, finds the comment in that thread and we get the output of that specific comment, this is optional
        DB = client["threads-relations"]
        relations_collection = DB.relations
        fetchCommentId = ObjectId(fetchComment)

        try:
            if fetchComment:
                DB = client[os.getenv("DB_NAME")]
                specific_thread = DB.companies
                specific_comment = relations_collection.find({"username":username},
                                                             {"thread_id":fetchCommentId})
                return #user_comment_list
            else:
                user_comment = relations_collection.find({"username":username}).limit(items)
                user_comment_list = list(user_comment)
                return user_comment_list
        except OperationFailure as e:
            return {"error":f"Something went wrong: {e}"}
    #---------------------Under construction---------------------

    def fetchCompanyProfile(self, company_name, items=10):
        DATABASE = os.getenv("DB_NAME")
        db = client[DATABASE]
        company_profile = db.companies

        try:
            company = company_profile.find({"company_name": company_name}).limit(items)
            company_list = list(company)

            def get_structure(obj, top_level=False):
                if isinstance(obj, dict):
                    if top_level:
                        return {
                            k: v if k in ['_id', 'company_name', 'org_number', 'company_info'] 
                            else get_structure(v) 
                            for k, v in obj.items()
                        }
                    else:
                        return {k: get_structure(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [get_structure(v) for v in obj[:1]] if obj else []
                elif isinstance(obj, ObjectId):
                    return str(obj)
                else:
                    return type(obj).__name__

            structure = [get_structure(doc, top_level=True) for doc in company_list]

            class ObjectEncoder(JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, ObjectId):
                        return str(obj)
                    return JSONEncoder.default(self, obj)
            
            return loads(dumps(structure, cls=ObjectEncoder))

        except OperationFailure as e:
            return {"error": f"Something went wrong: {e}"}




#---------------------------------------EXAMPLE USAGE---------------------------------------------------------------


"""mongo_test = MongoDatabaseHandler()

print(mongo_test.createCompanyProfile(org_number="556321-3692"))
"""
"""long_string = (
    "This is a very long string. This string is designed to be long and contains some comprehensible text. "
    "The purpose of this long string is to repeat certain words. Words like 'long', 'string', and 'text' are "
    "repeated many times to demonstrate the length and repetition. In this string, you will find that the word "
    "'string' appears frequently. This repetition is intentional. The goal is to make the string long and filled "
    "with repeated words. When working with long strings, it's common to encounter repetition. This string is a "
    "good example of that. As you read through this string, you will notice that certain words are repeated. "
    "These words include 'long', 'string', and 'repeated'. This is a very long string. This long string serves "
    "as an example of how to create a long string with repeated words. The string is not only long but also "
    "demonstrates repetition. This repetition makes the string longer and emphasizes certain words. When you see "
    "a long string like this, you can understand how repetition works in a text. This is the end of the long string."
)

try:
    data = InsertData(username="Bertil",
                  thread_text=long_string,
                  category="jobb",
                  company_profile="telenor-sverige-aktiebolag",
                  
                    )
except ValidationError as e:
    print(f"Validation error:{e}")

testar = MongoDatabaseHandler()

try:
    response = testar.insertDataThreads(title_text="fagget",
                                        username=data.username,
                                        
                                        thread_text=data.thread_text,
                                        
                                        company_profile=data.company_profile,
                                        
                                        category=data.category)
    print(response)

except ValidationError as e:
    print(f"Validation error{e}")"""




"""data = InsertData(
    company_profile="fag-Sverige-Aktiebolag"
)

test = MySQLHandler()
"""

"""mongo_test = MongoDatabaseHandler()

print(mongo_test.createCompanyProfile(org_number="556435-9981"))"""

"""async def main():
    checker = CompanyChecker()
    await checker.initialize()
    try:
        org_nummer = "556421-0309"  # Example organization number
        company_name = await checker.check_company_existence(org_nummer)
        if company_name:
            print(f"Company exists: {company_name}")
        else:
            print("Company does not exist")
    finally:
        await checker.close()

if __name__ == "__main__":
    asyncio.run(main())"""
#print(test.registerUser(password="password0",username="banan0",email="abdi_0@gmail.com"))
#print(test.create_table_query())
#print(test.registerUser(username="banan1",password="password1",email="abdi_1@gmail.com"))

"""
for i in range(4):
    print(lol.registerUser(username=f"banan{i}",password=f"password{i}",email=f"abdi_{i}@gmail.com"))
"""


"""print(testar.insertDataThreads())
print(testar.insertDataThreads("Kalle",long_string,database="Telenor-AB"))"""
#-----------------------------------------------------------------------------------------------------------------------





user = MongoDatabaseHandler()
print(user.insertDataComments(
    company_profile="magnussons-fisk-ab",
    thread_id="6689bb8ed93beba432879354",
    commenter="Gordita",
    comment_text="bing bingo bingo"
))


"""data = InsertData(company_profile="telenor-sverige-aktiebolag")

struct = user.fetchCompanyProfile(data.company_profile)

print(dumps(struct,indent=4))"""
 

"""user = MongoDatabaseHandler()

result = user.createCompanyProfile(org_number="556436-6739")

print(result)"""

"""user = MongoDatabaseHandler()

user.insertDataComments(company_profile=)"""