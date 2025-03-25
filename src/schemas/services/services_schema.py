from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ServiceModel(BaseModel):
    name: str
    price: int
    icon_svg: str
    custom: Optional[bool] = None
    plan_id: int
    

class ServiceResponse(BaseModel):
    id: int

    name: str
    price: int
    icon_svg: str
    custom: Optional[bool] = None
    plan_id: int
    
    
    created_at: datetime
    updated_at: datetime