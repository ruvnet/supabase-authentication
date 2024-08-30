from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: str
    email: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    age: Optional[int] = None
    theme: Optional[str] = "light"
    notifications: Optional[bool] = True
    language: Optional[str] = "en"

class Settings(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    age: Optional[int] = None
    theme: Optional[str] = "light"
    notifications: Optional[bool] = True
    language: Optional[str] = "en"

class UserCreate(BaseModel):
    email: str
    password: str
