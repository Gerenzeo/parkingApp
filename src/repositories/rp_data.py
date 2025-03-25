import json
from typing import Type, TypeVar, Optional, Dict
from datetime import datetime

from pydantic import BaseModel
from sqlalchemy import select, func, delete, update
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.declarative import DeclarativeMeta
from fastapi.encoders import jsonable_encoder

from src.db.db import async_session

T = TypeVar("T", bound=DeclarativeMeta)
S = TypeVar("S", bound=BaseModel)

SUB_T = TypeVar("SUB_T", bound=DeclarativeMeta)
SUB_S = TypeVar("SUB_S", bound=BaseModel)


class DataRepository:
    
    model: Type[T] = None
    sub_model: Type[SUB_T] = None

    schema: Type[S] = None
    sub_schema: Type[SUB_S] = None

    related_attrs: list[str] = []

    @classmethod
    def model_to_dict(cls, model_instance):
        return {column.name: getattr(model_instance, column.name) for column in model_instance.__table__.columns}


    @classmethod
    def validate_class_attrs(cls):
        """Check, model and schema exist."""
        if cls.model is None or cls.schema is None:
            raise NotImplementedError(f"Не указана модель или схема в {cls.__name__}")

    @classmethod
    async def create(cls, body: S) -> T:
        """Create data to database."""
        cls.validate_class_attrs()

        if not isinstance(body, cls.schema):
            raise ValueError(f"Переданный объект не является экземпляром {cls.schema}")

        async with async_session() as session:
            new_data = cls.model(**body.model_dump())

            session.add(new_data)
            await session.commit()
            await session.refresh(new_data)
            return new_data
    
    @classmethod
    async def bulk_create(cls, bodies: list[S]) -> list[T]:
        """Create multiple records in the database efficiently."""
        cls.validate_class_attrs()

        if not all(isinstance(body, cls.schema) for body in bodies):
            raise ValueError(f"Все объекты должны быть экземплярами {cls.schema}")

        async with async_session() as session:
            new_data = [cls.model(**body.model_dump()) for body in bodies]

            session.add_all(new_data)  # Добавляем сразу все объекты
            await session.commit()

            for data in new_data:
                await session.refresh(data)  # Обновляем из БД

            return new_data

    @classmethod
    async def bulk_update(cls, updates: list[dict]) -> list[T]:
        """Update multiple records in the database efficiently."""
        cls.validate_class_attrs()

        async with async_session() as session:
            for update_data in updates:
                obj_id = update_data.pop("id", None)
                if obj_id is None:
                    raise ValueError("Each update must contain an 'id' field")

                stmt = (
                    update(cls.model)  # Correct usage of the `update` function
                    .where(cls.model.id == obj_id)
                    .values(**update_data)  # Apply the update values
                    .execution_options(synchronize_session="fetch")
                )
                await session.execute(stmt)

            await session.commit()

            updated_ids = [upd.get("id") for upd in updates if "id" in upd]
            stmt = select(cls.model).where(cls.model.id.in_(updated_ids))
            result = await session.execute(stmt)

            return result.scalars().all()


    
    @classmethod
    async def update_data(cls, data_id: int, body: S) -> T | None:
        """Update record in database"""
        cls.validate_class_attrs()

        if not isinstance(body, cls.schema):
            raise ValueError(f"Переданный объект не является экземпляром {cls.schema}")

        async with async_session() as session:
            stmt = (
                update(cls.model)
                .where(cls.model.id == data_id)
                .values(jsonable_encoder(body, exclude_unset=True))
                .returning(cls.model)
            )
            result = await session.execute(stmt)
            updated_data = result.scalar_one_or_none()

            if updated_data:
                await session.commit()
                return updated_data

        return None
    
    @classmethod
    async def update_data_by_fields(cls, data_id: int, update_fields: Dict[str, any]):
        """Find object by ID and update specified fields dynamically"""
        cls.validate_class_attrs()

        async with async_session() as session:
            obj = await session.get(cls.model, data_id)
            if not obj:
                return None  # Объект не найден

            # Перебираем все переданные поля и обновляем их
            for key, value in update_fields.items():
                if hasattr(obj, key):  # Проверяем, что поле есть в модели
                    setattr(obj, key, value)

            await session.commit()
            await session.refresh(obj)  # Обновляем объект после коммита
            return obj  # Возвращаем обновленный объект
        
    @classmethod
    async def get_by_id(cls, item_id: int) -> T | None:
        """Get record by id"""
        cls.validate_class_attrs()

        async with async_session() as session:
            return await session.get(cls.model, item_id)
    
    @classmethod
    async def get_data(cls):
        """Get all data with joinload"""
        cls.validate_class_attrs()

        async with async_session() as session:
            query = select(cls.model)

            # Автоматически добавляем join для связанных таблиц
            for attr in cls.related_attrs:
                query = query.options(joinedload(getattr(cls.model, attr)))

            result = await session.execute(query)
            
            # Используем .unique(), чтобы избежать дубликатов
            return result.unique().scalars().all()
        
    @classmethod
    async def get_data_order_by(cls, value: str):
        """Get all data ordered by a specific field with joinload"""
        cls.validate_class_attrs()

        async with async_session() as session:
            query = select(cls.model)

            # Автоматически добавляем join для связанных таблиц
            for attr in cls.related_attrs:
                query = query.options(joinedload(getattr(cls.model, attr)))

            # Добавляем сортировку по переданному полю
            if hasattr(cls.model, value):  
                query = query.order_by(getattr(cls.model, value))
            else:
                raise ValueError(f"Модель {cls.model.__name__} не имеет поля '{value}'")

            result = await session.execute(query)
            
            return result.unique().scalars().all()
        
    @classmethod
    async def get_list_data_ordered_by(cls, by: str):
        """Get all data with joinload"""
        cls.validate_class_attrs()

        async with async_session() as session:
            query = select(cls.model)

            # Автоматически добавляем join для связанных таблиц
            for attr in cls.related_attrs:
                query = query.options(joinedload(getattr(cls.model, attr)))

            if by:
                if hasattr(cls.model, by):
                    query = query.order_by(getattr(cls.model, by))
                else:
                    raise ValueError(f"Модель {cls.model.__name__} не имеет поля '{by}' для сортировки")

            result = await session.execute(query)
            
            # Используем .unique(), чтобы избежать дубликатов
            return result.unique().scalars().all()

    @classmethod
    async def get_list_data_by(cls, field: str, value: str):
        """Get all data with joinload"""
        cls.validate_class_attrs()

        async with async_session() as session:
            query = select(cls.model)

            # Автоматически добавляем join для связанных таблиц
            for attr in cls.related_attrs:
                query = query.options(joinedload(getattr(cls.model, attr))).where(getattr(cls.model, field) == value)
            
            result = await session.execute(query)
            
            # Используем .unique(), чтобы избежать дубликатов
            return result.unique().scalars().all()
        
    @classmethod
    async def get_json_data_by(cls, field: str, value: str):
        """Get json data with joinload"""
        cls.validate_class_attrs()

        async with async_session() as session:
            query = select(cls.model)

            # Автоматически добавляем join для связанных таблиц
            for attr in cls.related_attrs:
                query = query.options(joinedload(getattr(cls.model, attr))).where(getattr(cls.model, field) == value)
            
            result = await session.execute(query)
            
            # Используем .unique(), чтобы избежать дубликатов
            data = result.unique().scalars().all()

            # json_data = [cls.model.model_validate(data_model) for data_model in data]
            json_data = [cls.schema.model_validate(cls.model_to_dict(data_model)) for data_model in data]
            return jsonable_encoder(json_data)
    
    @classmethod
    async def get_list_data_by_with_order(cls, field: str, value: str, by: str = None):
        """Get all data filtered by field with optional ordering"""
        cls.validate_class_attrs()

        async with async_session() as session:
            query = select(cls.model)

            # Автоматически добавляем join для связанных таблиц
            for attr in cls.related_attrs:
                query = query.options(joinedload(getattr(cls.model, attr)))

            # Добавляем фильтр по полю, если оно существует
            if hasattr(cls.model, field):
                query = query.where(getattr(cls.model, field) == value)
            else:
                raise ValueError(f"Модель {cls.model.__name__} не имеет поля '{field}'")

            # Добавляем сортировку, если передано поле "by"
            if by:
                if hasattr(cls.model, by):
                    query = query.order_by(getattr(cls.model, by))
                else:
                    raise ValueError(f"Модель {cls.model.__name__} не имеет поля '{by}' для сортировки")

            result = await session.execute(query)
            
            return result.unique().scalars().all()

    @classmethod
    async def get_data_with_pagination(cls, skip: int = 0, limit: int = 10):
        """Get all data with pagination"""
        cls.validate_class_attrs()

        if skip < 0 or limit <= 0:
            raise ValueError("Параметры пагинации должны быть положительными, и limit не может быть равен нулю.")

        try:
            async with async_session() as session:
                query = select(cls.model).offset(skip).limit(limit)
                result = await session.execute(query)
                return result.scalars().all() 
        except Exception as e:
            # Логирование ошибки или её обработка
            raise RuntimeError(f"Error fetch data: {e}")
        
    @classmethod
    async def get_data_with_pagination_by(cls, by: dict = None, skip: int = 0, limit: int = 10):
        """Получает данные с пагинацией и фильтрацией по полям из `by`"""
        cls.validate_class_attrs()

        if skip < 0 or limit <= 0:
            raise ValueError("Параметры пагинации должны быть положительными, и limit не может быть равен нулю.")

        try:
            query = select(cls.model)  # Начинаем с базового запроса

            # Фильтрация по `by`
            if by:
                for key, value in by.items():
                    query = query.where(getattr(cls.model, key) == value)

            query = query.offset(skip).limit(limit)  # Применяем пагинацию

            async with async_session() as session:  # Используем правильную сессию
                result = await session.execute(query)
                return result.scalars().all()

        except Exception as e:
            raise RuntimeError(f"Error fetching data: {e}")


    @classmethod
    async def get_total_count(cls) -> int:
        """Total records in db"""
        async with async_session() as session:
            query = select(func.count()).select_from(cls.model)
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def get_data_by(cls, field: str, value: str):
        """Получить запись по указанному полю, с загрузкой связанных данных"""
        cls.validate_class_attrs()

        async with async_session() as session:
            query = select(cls.model).where(getattr(cls.model, field) == value)

            # Добавляем подгрузку связанных данных
            for attr in cls.related_attrs:
                query = query.options(joinedload(getattr(cls.model, attr)))

            result = await session.execute(query)
            return result.unique().scalar_one_or_none()
        
    @classmethod
    async def delete_by(cls, field: str, value: str):
        """Удалить запись по указанному полю"""
        cls.validate_class_attrs()

        async with async_session() as session:
            stmt = delete(cls.model).where(getattr(cls.model, field) == value)

            # Выполнение запроса на удаление
            result = await session.execute(stmt)
            await session.commit()

            return result.rowcount
        

    @classmethod
    async def delete_all_data(cls, field: str, values: int | list[int]):
        """Удалить записи, где `field` совпадает с одним из `values`"""
        cls.validate_class_attrs()

        # Если передано одно число, превращаем в список
        if isinstance(values, int):
            values = [values]

        async with async_session() as session:
            stmt = delete(cls.model).where(getattr(cls.model, field).in_(values))

            result = await session.execute(stmt)
            await session.commit()

            return result.rowcount
