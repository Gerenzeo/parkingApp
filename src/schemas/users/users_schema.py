from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class UserModel(BaseModel):
    unique_code: str
    full_name: str
    email: str
    phone: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    password: str
    role_id: int

class UserResponse(BaseModel):
    id: int
    unique_code: str
    full_name: str
    email: str
    phone: str
    password: str
    role_id: int
    day_night_mode: bool
    created_at: datetime
    updated_at: datetime