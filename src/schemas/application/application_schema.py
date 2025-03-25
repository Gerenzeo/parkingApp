from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ApplicationModel(BaseModel):
    is_active: bool

class ApplicationResponse(BaseModel):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime