from typing import Type
from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import OperationalError
from fastapi.encoders import jsonable_encoder

from src.db.db import async_session
from src.repositories.rp_data import DataRepository
from src.db.models import PlaceService
from src.schemas.places.places_schema import  PlaceServiceModel


class PlaceServiceRepository(DataRepository):
    model: Type[PlaceService] = PlaceService
    schema: Type[PlaceServiceModel] = PlaceServiceModel

    related_attrs = ["service"]

oPlaceServices = PlaceServiceRepository()