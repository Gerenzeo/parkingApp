from typing import List
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Integer, DateTime, func, String, Boolean, ForeignKey, Text

from src.db.db import engine

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

class BaseWithTimestamps(Base):
    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

# APP
class Application(BaseWithTimestamps):
    __tablename__ = "application"


    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

# ROLES
class Role(BaseWithTimestamps):
    __tablename__ = "roles"

    role_name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    role_name_code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    
# USERS
class User(BaseWithTimestamps):
    __tablename__ = "users"

    unique_code: Mapped[str] = mapped_column(String(150), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(150), nullable=True)
    country: Mapped[str] = mapped_column(String(50), nullable=True)
    city: Mapped[str] = mapped_column(String(50), nullable=True)
    phone: Mapped[str] = mapped_column(String(25), nullable=True)
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    balance: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    card_number: Mapped[str] = mapped_column(String(19), nullable=True)
    card_expired_date: Mapped[str] = mapped_column(String(10), nullable=True)
    card_cvv: Mapped[int] = mapped_column(Integer, nullable=True)
    activity: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    refresh_token: Mapped[str] = mapped_column(String(255), nullable=True)
    day_night_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False)

    count_place: Mapped[int] = mapped_column(Integer, nullable=True)

    role_id: Mapped[int] = mapped_column(Integer, ForeignKey("roles.id"), nullable=False)
    role: Mapped["Role"] = relationship("Role")

    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("plans.id"), nullable=True)
    plan: Mapped["Plan"] = relationship("Plan", back_populates="users")

    places: Mapped[List["Place"]] = relationship("Place", back_populates="user", foreign_keys="[Place.user_id]")
    clients: Mapped[List["Client"]] = relationship("Client", back_populates="user")


# SERVICE
class Service(BaseWithTimestamps):
    __tablename__ = "services"

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    icon_svg: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    custom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)

    plan_id: Mapped[int] = mapped_column(Integer, ForeignKey("plans.id", ondelete="CASCADE"), nullable=False)
    plan: Mapped["Plan"] = relationship("Plan", back_populates="services")


# PLAN
class Plan(BaseWithTimestamps):
    __tablename__ = "plans"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    users: Mapped[List["User"]] = relationship("User", back_populates="plan")
    services: Mapped[List["Service"]] = relationship("Service", back_populates="plan", cascade="all, delete")

# PLACE SERVICE
class PlaceService(BaseWithTimestamps):
    __tablename__ = "place_services"

    place_id: Mapped[int] = mapped_column(Integer, ForeignKey("places.id", ondelete="CASCADE"), nullable=False)
    service_id: Mapped[int] = mapped_column(Integer, ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    service_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    place: Mapped["Place"] = relationship("Place", back_populates="place_services")
    service: Mapped["Service"] = relationship("Service")

# PLACE
class Place(BaseWithTimestamps):
    __tablename__ = "places"

    unique_key: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    index: Mapped[int] = mapped_column(Integer, nullable=False)
    available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)
    
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)

    status_payment: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    price: Mapped[int] = mapped_column(Integer, nullable=True)
    
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship("User", back_populates="places", foreign_keys="[Place.user_id]")

    client_id: Mapped[int] = mapped_column(Integer, ForeignKey("clients.id"), nullable=True)
    client: Mapped["Client"] = relationship("Client")
    
    place_services: Mapped[List["PlaceService"]] = relationship("PlaceService", back_populates="place", cascade="all, delete")

# CLIENTS
class Client(BaseWithTimestamps):
    __tablename__ = "clients"

    unique_code: Mapped[str] = mapped_column(String(150), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=True)
    email: Mapped[str] = mapped_column(String(150), nullable=True)
    phone: Mapped[str] = mapped_column(String(25), nullable=True)

    car_brand: Mapped[str] = mapped_column(String(50), nullable=True)
    car_model: Mapped[str] = mapped_column(String(50), nullable=True)
    car_year: Mapped[str] = mapped_column(String(5), nullable=True)
    color: Mapped[str] = mapped_column(String(25), nullable=True)
    plate: Mapped[str] = mapped_column(String(40), nullable=True)

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    user: Mapped["User"] = relationship("User")




async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)