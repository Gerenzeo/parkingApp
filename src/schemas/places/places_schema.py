from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class PlaceModel(BaseModel):
    unique_key: str
    index: int
    available: bool
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: int

class PlaceResponse(BaseModel):
    id: int
    unique_key: str
    index: int
    available: bool
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    user_id: int
    created_at: datetime
    updated_at: datetime

class PlaceServiceModel(BaseModel):
    place_id: int
    service_id: int
    service_active: bool