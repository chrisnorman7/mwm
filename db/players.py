"""Provides the Player class."""

from sqlalchemy import Column, Boolean, Integer
from .base import (
    Base, NameMixin, DescriptionMixin, PasswordMixin, ExperienceMixin,
    LevelMixin, LocationMixin, StatisticsMixin
)


class StatProperty(property):
    """Get and set statistics in a dynamic fashion."""

    def __init__(self, name):
        self.name = name
        super().__init__(self.get, self.set)

    def get_max_value(self, instance):
        return getattr(instance, f'max_{self.name}')

    def get(self, instance):
        value = getattr(instance, self.name)
        if value is None:
            return self.get_max_value(instance)
        return value

    def set(self, instance, value):
        if value >= self.get_max_value(instance):
            value = None
        setattr(instance, self.name, value)


class Player(
    Base, NameMixin, DescriptionMixin, PasswordMixin, ExperienceMixin,
    LevelMixin, LocationMixin, StatisticsMixin
):
    """A player instance."""

    __tablename__ = 'players'
    builder = Column(Boolean, nullable=False, default=False)
    admin = Column(Boolean, nullable=False, default=False)
    mobile = Column(Boolean, nullable=False, default=False)
    hitpoints = Column(Integer, nullable=True)
    mana = Column(Integer, nullable=True)
    endurance = Column(Integer, nullable=True)


for name in ('hitpoints', 'mana', 'endurance'):
    setattr(Player, name[0], StatProperty(name))
