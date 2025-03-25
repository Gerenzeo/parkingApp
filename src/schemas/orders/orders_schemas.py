from datetime import datetime
from pydantic import BaseModel


class OrderPlanModel(BaseModel):
    name: str
    price: int

class OrderPlanResponse(BaseModel):
    id: int
    name: str
    price: int
    created_at: datetime
    updated_at: datetime