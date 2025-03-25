from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ClientModel(BaseModel):
    unique_code: str
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: str
    car_brand: Optional[str] = None
    car_model: Optional[str] = None
    car_year: Optional[str] = None
    color: Optional[str] = None
    plate: Optional[str] = None
    user_id: int

class ClientResponse(BaseModel):
    id: int
    unique_code: str
    first_name: str
    last_name: str
    email: str
    phone: str
    car_brand: str
    car_model: str
    car_year: str
    color: str
    plate: str
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True