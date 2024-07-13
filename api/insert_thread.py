from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ValidationError,field_validator
from typing import Optional
from database_logic.database_handler import MongoDatabaseHandler
import re

#TODO: Add some security with JWT, making sure that only logged in users can interact with the platform

class ThreadData(BaseModel):
    username: str = Field(..., max_length=25)
    thread_text: str = Field(..., min_length=500, max_length=6000)
    title_text: str = Field(..., min_length=10, max_length=60)
    category: str = Field(...)
    company_profile: str = Field(...)

    @field_validator("title_text")                                                                                           
    @classmethod                                                                                                             
    def validate_title_text(cls,value):                                                                                      
        if value is None:                                                                                                    
            raise ValueError("Title text can not be None")                                                                   
        lenght = len(value)                                                                                                  
        if lenght < 10:                                                                                                      
            raise ValueError("Title text is too short")
        
    @field_validator("thread_text")                                                                                          
    @classmethod                                                                                                             
    def validate_thread_text(cls,value):                                                                                     
        if value is not None:                                                                                                
            if len(value) < 500:                                                                                             
                raise ValueError("Thread text is too short")                                                                 
        else:                                                                                                                
            raise ValueError("Thread text can not be None")                                                                  
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

class InsertThread:
    def __init__(self, endpoint: str = "/api/v1/insert-thread"):
        self.endpoint = endpoint
        self.db_handler = MongoDatabaseHandler()

    def create_endpoint(self, app: FastAPI):
        @app.post(self.endpoint)
        async def insert_thread(data: ThreadData):
            try:
                result = self.db_handler.insertDataThreads(
                    title_text=data.title_text,
                    username=data.username,
                    thread_text=data.thread_text,
                    category=data.category,
                    company_profile=data.company_profile
                )
                return {"message": "Data inserted successfully", "result": result}
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"An error occurred while inserting data: {str(e)}")

# Usage in your main FastAPI app file:
"""app = FastAPI()
insert_thread = InsertThread()
insert_thread.create_endpoint(app)"""