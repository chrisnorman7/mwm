"""Provides the Room class."""

from sqlalchemy import Column, Boolean, Integer
from .base import Base, NameMixin, DescriptionMixin


class Room(Base, NameMixin, DescriptionMixin):
    """A room instance."""

    __tablename__ = 'rooms'
    lit = Column(Boolean, nullable=False, default=True)
    safe = Column(Boolean, nullable=False, default=False)
    regain = Column(Integer, nullable=False, default=1)
