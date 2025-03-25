from typing import Type
from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import OperationalError
from fastapi.encoders import jsonable_encoder

from src.db.db import async_session
from src.db.models import Role
from src.repositories.rp_data import DataRepository
from src.schemas.roles.roles_schema import RoleModel



class RoleRepository(DataRepository):
    model: Type[Role] = Role
    schema: Type[RoleModel] = RoleModel


oRoles = RoleRepository()