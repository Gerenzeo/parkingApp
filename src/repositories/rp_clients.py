from typing import Type
from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import OperationalError
from fastapi.encoders import jsonable_encoder

from src.db.db import async_session
from src.db.models import Client
from src.repositories.rp_data import DataRepository
from src.schemas.clients.clients_schema import ClientModel



class ClientRepository(DataRepository):
    model: Type[Client] = Client
    schema: Type[ClientModel] = ClientModel


oClients = ClientRepository()