from typing import Optional
from sqlalchemy import ForeignKey, Integer, String, select, Column
from sqlalchemy.orm import relationship, Mapped
from openg2p_fastapi_common.models import BaseORMModelWithTimes
from sqlalchemy.ext.asyncio import async_sessionmaker
from openg2p_fastapi_common.context import dbengine

from .strategy import Strategy
from ..schemas import LevelTypeEnum


class DfspLevel(BaseORMModelWithTimes):
    __tablename__ = "dfsp_levels"

    name: Mapped[str] = Column(String)
    level_type: Mapped[str] = Column(String(20), default=LevelTypeEnum)
    parent: Mapped[Optional[int]] = Column(Integer, nullable=True)

    class Config:
        orm_mode = True

    @classmethod
    async def get_level(cls, **kwargs):
        response = []
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = select(cls)
            for key, value in kwargs.items():
                if value is not None:
                    stmt = stmt.where(getattr(cls, key) == value)

            stmt = stmt.order_by(cls.id.asc())

            result = await session.execute(stmt)

            response = list(result.scalars())
        return response


class DfspLevelValue(BaseORMModelWithTimes):
    __tablename__ = "dfsp_level_values"

    name: Mapped[str] = Column(String)
    code: Mapped[str] = Column(String(20))
    description: Mapped[Optional[str]] = Column(String, nullable=True)
    parent: Mapped[Optional[int]] = Column(Integer, nullable=True)
    level_id: Mapped[int] = Column(Integer, nullable=True)
    strategy_id: Mapped[Optional[int]] = Column(
        Integer, ForeignKey("strategy.id"), nullable=True
    )

    strategy: Mapped[Optional[Strategy]] = relationship("Strategy")
    validation_regex: Mapped[Optional[str]] = Column(String, nullable=True)

    class Config:
        orm_mode = True

    @classmethod
    async def get_level_values(cls, **kwargs):
        response = []
        async_session_maker = async_sessionmaker(dbengine.get())
        async with async_session_maker() as session:
            stmt = select(cls)
            for key, value in kwargs.items():
                if value is not None:
                    stmt = stmt.where(getattr(cls, key) == value)

            stmt = stmt.order_by(cls.id.asc())

            result = await session.execute(stmt)

            response = list(result.scalars())
        return response
