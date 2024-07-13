from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, Field, ValidationError,field_validator
from database_logic.database_handler import MongoDatabaseHandler
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from OpenSSL import crypto


secret_key = crypto.PKey()


SECRET_KEY = secret_key.generate_key(crypto.TYPE_RSA,2048)



class AuthUserData(BaseModel):
    username:str = Field(...,max_length=25)
    password:str = Field(...)

class AuthenticateUser:
    pass



#This is supposed to be a class or something