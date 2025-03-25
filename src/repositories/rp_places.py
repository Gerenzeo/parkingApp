from typing import Type
from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import OperationalError
from fastapi.encoders import jsonable_encoder

from src.db.db import async_session
from src.repositories.rp_data import DataRepository
from src.db.models import Place
from src.schemas.places.places_schema import PlaceModel


class PlaceRepository(DataRepository):
    model: Type[Place] = Place
    schema: Type[PlaceModel] = PlaceModel

    related_attrs = ["user", "place_services"]

oPlaces = PlaceRepository()