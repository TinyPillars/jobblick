from pymongo import MongoClient
import os
from dotenv import load_dotenv
import datetime
from pydantic import BaseModel,ValidationError, field_validator,Field,validator
from typing import Literal
from tags_algorithm import tagging_algorithm
from json import dumps
from pymongo.errors import OperationFailure
load_dotenv()

uri = os.getenv("MONGO_URL")
client = MongoClient(uri)
#DATABASE = os.getenv("DB_NAME")
#db = client[DATABASE]
#collection = db["threads"]


class InsertData(BaseModel):
    username:str = Field(...,max_length=14)
    thread_text:str = Field(...,max_length=6000)
    category:Literal["jobb", "lön","arbetsmiljö","arbetsgivare","kultur"]
    database_name:str

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
            raise ValueError(f"Lenght of array:{value} exceeds 1 ,use '-' for each word in a company name")
        value = str(value)
        value = value.replace("'","")
        value = value.replace("[","")
        value = value.replace("]","")

        if "-" not in value:
            raise ValueError("Must contain '-'")
        return value
    
    
class MongoDatabaseHandler:

    def __init__(self):
        super().__init__()

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

        try:
            response = dumps("Data succesfully inserted")
            return response

        except OperationFailure as e:
            return {f"Something went wrong:\n{e}"}

    def insertDataComments():
        pass  

    def fetchData(self):
        pass

    def createDatabase(self):
        pass

    def fetchDatabase(self):
        pass




#---------------------------------------EXAMPLE USAGE---------------------------------------------------------------
long_string = (
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




"""print(testar.insertDataThreads())
print(testar.insertDataThreads("Kalle",long_string,database="Telenor-AB"))"""
#-----------------------------------------------------------------------------------------------------------------------