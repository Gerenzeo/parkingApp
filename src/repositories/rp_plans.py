from typing import Type
from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import OperationalError
from fastapi.encoders import jsonable_encoder

from src.db.db import async_session
from src.db.models import Plan
from src.repositories.rp_data import DataRepository
from src.schemas.plans.plans_schema import PlanModel


class PlanRepository(DataRepository):
    model: Type[Plan] = Plan
    schema: Type[PlanModel] = PlanModel


    related_attrs = ["services"]

oPlans = PlanRepository()