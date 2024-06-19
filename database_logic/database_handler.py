from pymongo import MongoClient
import os
from dotenv import load_dotenv
import datetime
from pydantic import BaseModel,ValidationError, validator,Field
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
    comment:str = Field(...,max_length=2500)

    @validator("thread_text")
    def validate_thread_text(cls,value):
        if not value:
            raise ValueError("Thread text can not be empty")
        elif len(value) < 500:
            raise ValueError("Thread text is too short")
        return value
    
    @validator("comment")
    def validate_comment_text(cls,value):
        if not value:
            raise ValueError("Comment text can not be empty")
        if len(value) < 10:
            raise ValueError("Comment text is to short")
        return value
    
class MongoDatabaseHandler:

    def __init__(self):
        pass

    def insertDataThreads(self,database:str, data:InsertData):
        tags:list = tagging_algorithm(data.thread_text).generate_tags(5)
        data_payload = {
            "username":data.username,
            "thread_text":data.thread_text,
            "tags":tags,
            "timestamp":datetime.datetime.now(tz=datetime.timezone.utc),
            "comments":[{}]
        }
        DATABASE = database
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



testar = MongoDatabaseHandler()

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
print(testar.insertDataThreads("Kalle",long_string,database="Telenor-AB"))
