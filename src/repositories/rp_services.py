from typing import Type
from datetime import datetime

from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import OperationalError
from fastapi.encoders import jsonable_encoder

from src.db.db import async_session
from src.db.models import Service
from src.repositories.rp_data import DataRepository
from src.schemas.services.services_schema import ServiceModel


class ServiceRepository(DataRepository):
    model: Type[Service] = Service
    schema: Type[ServiceModel] = ServiceModel

oServices = ServiceRepository()