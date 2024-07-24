from pydantic import BaseModel, EmailStr
from typing import Optional



class UserBase(BaseModel):    
    email: EmailStr
    name: str
    hp: str

class UserCreate(UserBase):
    userid: str
    password: str

class UserInDB(UserBase):
    userid: str
    hashed_password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    userid: Optional[str] = None

class UserDeleteRequest(BaseModel):
    userid: str

class Result(BaseModel):
	line1: str
	line2: str
	line3: str
	line4: str
	line5: str
	line6: str
	line7: str