import uuid
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: str
    profile_picture: Optional[str]

class UserRole(str):
    ADMIN = "admin"
    USER = "user"

class UserCreate(UserBase):
    email: EmailStr
    password: str
    name: str
    profile_picture: Optional[str]

class UserUpdate(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    role: Optional[str]
    profile_picture: Optional[str]

class UserLogin(BaseModel):
    email: EmailStr
    password: str