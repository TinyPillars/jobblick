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
from disposable_email_domains import blocklist
load_dotenv()

uri = os.getenv("MONGO_URL")
client = MongoClient(uri)
#DATABASE = os.getenv("DB_NAME")
#db = client[DATABASE]
#collection = db["threads"]


class InsertData(BaseModel):
    username:Optional[str] = Field(...,max_length=14)
    email:Optional[EmailStr]
    thread_text:Optional[str] = Field(...,max_length=6000)
    category:Optional[Literal["jobb", "lön","arbetsmiljö","arbetsgivare","kultur"]]
    database_name:Optional[str]
    star_ratings:Optional[Literal[1,2,3,4,5]]

    @field_validator("thread_text")
    @classmethod
    def validate_thread_text(cls,value):
        if not value:
            raise ValueError("Thread text can not be empty")
        elif len(value) < 500:
            raise ValueError("Thread text is too short")
        return value
    
    @field_validator("database_name")
    @classmethod
    def validate_db_name(cls,value):
        value  = [i for i in value.split()]
        if len(value)>1:
            raise ValueError(f"Lenght of array (company name/database name):{value} exceeds 1, use '-' for each word in a company name")
        value = str(value)
        value = value.replace("'","")
        value = value.replace("[","")
        value = value.replace("]","")

        if "-" not in value:
            raise ValueError("Company name/database name must contain '-'")

        value_ = bool(re.search(r"\s"),value)
        
        if value_:
            raise ValueError("Company name/database name can not contain spaces")
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

        
    def username_thread_relation(self,username):
        pass

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
    def insertDataThreads(self, data:InsertData):
        tags:list = tagging_algorithm(data.thread_text).generate_tags(5)
        data_payload = {
            "username":data.username,
            "thread_text":data.thread_text,
            "tags":tags,
            "timestamp":datetime.datetime.now(tz=datetime.timezone.utc),
            "category":data.category,
            "comments":[{}]
        }
        DATABASE = data.database_name
        db = client[DATABASE]
        thread = db.threads
        thread.insert_one(data_payload)
        client.close()

        try:
            response = dumps("Data succesfully inserted")
            return response

        except OperationFailure as e:
            return {f"Something went wrong:\n{e}"}   
    #TODO We need to somehow connect a specific thread with the correct comments comments, best way of doing this could be to get the objectId for a thread document
    def insertDataComments():
        pass  

    def fetchData(self):
        pass

    def createDatabase(self):
        pass

    def fetchDatabase(self):
        pass




#---------------------------------------EXAMPLE USAGE---------------------------------------------------------------
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
    data = InsertData(username="Kalle",
                  thread_text=long_string,
                  category="jobb",
                  database_name="Telenor-AB",
                  
                    )
except ValidationError as e:
    print(f"Validation error:{e}")

testar = MongoDatabaseHandler()

try:
    response = testar.insertDataThreads(data)
    print(response)

except ValidationError as e:
    print(f"Validation error{e}")


"""

test = MySQLHandler()

#print(test.registerUser(password="password0",username="banan0",email="abdi_0@gmail.com"))
#print(test.create_table_query())
print(test.registerUser(username="banan1",password="password1",email="abdi_1@gmail.com"))

"""for i in range(4):
    print(lol.registerUser(username=f"banan{i}",password=f"password{i}",email=f"abdi_{i}@gmail.com"))
"""


"""print(testar.insertDataThreads())
print(testar.insertDataThreads("Kalle",long_string,database="Telenor-AB"))"""
#-----------------------------------------------------------------------------------------------------------------------