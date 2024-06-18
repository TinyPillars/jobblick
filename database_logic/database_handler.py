from pymongo import MongoClient
import os
from dotenv import load_dotenv
import datetime
from pydantic import BaseModel
from tags_algorithm import tagging_algorithm
from json import dumps
from pymongo.errors import OperationFailure
load_dotenv()

uri = os.getenv("MONGO_URL")
client = MongoClient(uri)
DATABASE = os.getenv("DB_NAME")
db = client[DATABASE]
collection = db["threads"]

class MongoDatabaseHandler(BaseModel):
    


    def __init__(self):
        pass

    def insertData(self,username:str,thread_text:str):
        tags:list = tagging_algorithm(thread_text).generate_tags(5)
        data_payload = {
            "username":username,
            "thread_text":thread_text,
            "tags":tags,
            "timestamp":datetime.datetime.now(tz=datetime.timezone.utc)
        }
        thread = db.threads
        thread.insert_one(data_payload)

        try:
            response = dumps("Data succesfully inserted")
            return response

        except OperationFailure as e:
            return {f"Something went wrong:\n{e}"}

    async def fetchData(self):
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
print(testar.insertData("Kalle",long_string))
