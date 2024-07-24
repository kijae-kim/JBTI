from pydantic import BaseModel, EmailStr

class User(BaseModel):
    
    userid: str
    email: EmailStr
    name: str
    hp: str
    password: str


class UserInDB(User):
    hashed_password: str

