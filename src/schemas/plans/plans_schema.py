from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class PlanModel(BaseModel):
    name: str
    code: str
    position: int

class PlanResponse(BaseModel):
    id: int
    
    name: str
    code: str
    position: int
    
    created_at: datetime
    updated_at: datetime
