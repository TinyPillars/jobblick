from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from pydantic import BaseModel, Field, ValidationError,field_validator,EmailStr
from database_logic.database_handler import MySQLHandler
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from OpenSSL import crypto
from disposable_email_domains import blocklist
from security.hex_generator import SecurityConfigGenerator
"""secret_key = crypto.PKey()
SECRET_KEY = secret_key.generate_key(crypto.TYPE_RSA,2048)"""

key_generator = SecurityConfigGenerator()
SECRET_KEY = key_generator.secret_key
ALGORITHM = key_generator.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=['bcrypt'],deprecated = "auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
app = FastAPI()





class AuthUserData(BaseModel):
    username:Optional[str] = Field(...,max_length=25)
    email:Optional[EmailStr] = None
    password:str = Field(...)

    @field_validator
    @classmethod
    def validate_email(cls,value):
        if value in blocklist:
            raise ValueError("Email belongs to blacklisted domains")
    
class Token(BaseModel):
    access_token:str
    token_type:str


class TokenData(BaseModel):
    username:str | None = None

class UserInDB(AuthUserData):
    hashed_email:Optional[str]
    hashed_password:str


def create_access_token(data:dict,expires_delta:timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire =datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token:str = Depends(oauth2_scheme)):
    pass

class AuthenticateUser:
    def __init__(self,endpoint:str = "/api/v1/auth-user"):
        self.endpoint = endpoint
        self.db_handler = MySQLHandler()

    def create_endpoint(self,app:FastAPI):
        @app.get(self.endpoint)
        async def auth_user(data:AuthUserData):
            try:
                if data.email:
                    result = self.db_handler.authenticate(
                        email=data.email,
                        password=data.password)
                    return {"message":"user successfully connected"}
                elif data.username:
                    result = self.db_handler.authenticate(
                        username=data.username,
                        password=data.password
                    )
                    return {"message":"user successfully connected"}
            except Exception as e:
                raise HTTPException(status_code=500,detail=f"An error has occurred while authenticating user: {str(e)}")   




