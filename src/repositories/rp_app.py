from typing import Type
from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import OperationalError
from fastapi.encoders import jsonable_encoder

from src.db.db import async_session
from src.db.models import Application
from src.repositories.rp_data import DataRepository
from src.schemas.application.application_schema import ApplicationModel



class ApplicationRepository(DataRepository):
    model: Type[Application] = Application
    schema: Type[ApplicationModel] = ApplicationModel






oApp = ApplicationRepository()