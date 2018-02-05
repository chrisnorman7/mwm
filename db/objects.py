"""Provides the Object class."""

from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import (
    Base, NameMixin, NameDescriptionMixin, LocationMixin, StatisticsMixin
)


class WearPosition(Base, NameMixin):
    """Where something can be worn."""

    __tablename__ = 'wear_positions'


class Object(Base, NameDescriptionMixin, LocationMixin, StatisticsMixin):
    """An object lying on the ground."""

    __tablename__ = 'objects'
    container = Column(Boolean, nullable=False, default=False)
    weapon = Column(Boolean, nullable=False, default=False)
    wear_position_id = Column(
        Integer, ForeignKey('wear_positions.id'), nullable=True
    )
    wear_position = relationship('WearPosition', backref='items')
    light = Column(Boolean, nullable=False, default=False)
    lit = Column(Boolean, nullable=False, default=False)
    drink = Column(Boolean, nullable=False, default=False)
    food = Column(Boolean, nullable=False, default=False)
    world_max = Column(Integer, nullable=True)
    parent_id = Column(Integer, ForeignKey('objects.id'), nullable=True)
    parent = relationship(
        'Object', backref='children', foreign_keys=[parent_id],
        remote_side='Object.id'
    )
    integer_1 = Column(Integer, nullable=True)
    integer_2 = Column(Integer, nullable=True)
    integer_3 = Column(Integer, nullable=True)
    integer_4 = Column(Integer, nullable=True)
    integer_5 = Column(Integer, nullable=True)
    string_1 = Column(String(150), nullable=True)
    string_2 = Column(String(150), nullable=True)
    string_3 = Column(String(150), nullable=True)
    string_4 = Column(String(150), nullable=True)
    string_5 = Column(String(150), nullable=True)
    inside_id = Column(Integer, ForeignKey('objects.id'), nullable=True)
    inside = relationship(
        'Object', backref='contains', foreign_keys=[inside_id],
        remote_side='Object.id'
    )
    holding_id = Column(Integer, ForeignKey('characters.id'), nullable=True)
    holding = relationship(
        'Character', backref='inventory', foreign_keys=[holding_id],
        remote_side='Character.id'
    )
    worn_id = Column(Integer, ForeignKey('characters.id'), nullable=True)
    worn = relationship(
        'Character', backref='wearing', foreign_keys=[worn_id],
        remote_side='Character.id'
    )
