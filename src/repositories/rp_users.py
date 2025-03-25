from typing import Type
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import OperationalError
from fastapi.encoders import jsonable_encoder

from src.db.db import async_session
from src.db.models import User, Role, Plan
from src.repositories.rp_data import DataRepository
from src.schemas.users.users_schema import UserModel, UserResponse


class UserRepository(DataRepository):
    model: Type[User] = User
    schema: Type[UserModel] = UserModel

    related_attrs = ["role", "places", "plan"]


oUsers = UserRepository()