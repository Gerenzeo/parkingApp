from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class RoleModel(BaseModel):
    role_name: str
    role_name_code: str

class RoleResponse(BaseModel):
    id: int
    role_name: str
    role_name_code: str
    created_at: datetime
    updated_at: datetime