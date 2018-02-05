"""Provides the Character class."""

from sqlalchemy import Column, Boolean, Integer
from .base import (
    Base, NameDescriptionMixin, PasswordMixin, ExperienceMixin, LevelMixin,
    LocationMixin, StatisticsMixin
)

connections = {}


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


class Character(
    Base, NameDescriptionMixin, PasswordMixin, ExperienceMixin, LevelMixin,
    LocationMixin, StatisticsMixin
):
    """A player instance."""

    __tablename__ = 'characters'
    builder = Column(Boolean, nullable=False, default=False)
    admin = Column(Boolean, nullable=False, default=False)
    mobile = Column(Boolean, nullable=False, default=False)
    hitpoints = Column(Integer, nullable=True)
    mana = Column(Integer, nullable=True)
    endurance = Column(Integer, nullable=True)

    @property
    def connection(self):
        return connections.get(self.id, None)

    @connection.setter
    def connection(self, connection):
        """Register this character as logged in."""
        if connection is None:
            if self.connection is not None:
                del connections[self.id]
            return
        if self.connection is not None:
            connection.notify('*** Booting old connection. ***')
            self.connection.notify(
                '*** Logging you in from somewhere else ***'
            )
            self.connection.object = self
            self.connection.transport.loseConnection()
        self.connection = connection
        self.notify(f'Welcome back, {self.name}.')

    def notify(self, string):
        """Send a string of text to this character."""
        if self.connection is not None:
            return self.connection.notify(string)


for name in ('hitpoints', 'mana', 'endurance'):
    setattr(Character, name[0], StatProperty(name))
