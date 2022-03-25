from pydantic import BaseModel, EmailStr
from typing import List, Literal, Optional
from datetime import datetime

class FetchMetaData(BaseModel):
    num_records: int
    pagination: int
    page: int
    division: int

class AddUser(BaseModel):
    first_name: str
    last_name: str
    gender: Literal["Male", "Female"]
    age: int
    email_address: EmailStr
    password: str

    class Config:
        orm_mode = True

class User(AddUser):
    user_id: int
    created_at: datetime

class GetUser(BaseModel):
    message: str
    user: Optional[User]

class GetUsers(BaseModel):
    message: str
    meta_data: Optional[FetchMetaData]
    users: Optional[List[User]]

class Auth(BaseModel):
    message: str
    access_token: str
    token_type: str
    user: Optional[User]