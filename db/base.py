"""Provides base classes and mixins."""

from passlib.hash import sha256_crypt as crypt
from random_password import random_password
from sqlalchemy import (
    Column, Integer, String, ForeignKey, inspect, DateTime, func, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from .engine import engine
from .session import Session


class _Base:
    """The base class for declarative."""

    id = Column(Integer, primary_key=True)
    created = Column(
        DateTime(timezone=True), nullable=False, default=func.now()
    )

    def notify(self):
        """Overridden for Character instances."""

    def __repr__(self):
        res = f'{self.__class__.__name__} ('
        strings = []
        for name in inspect(self.__class__).columns.keys():
            strings.append(f'{name}={getattr(self, name)}')
        return res + ', '.join(strings) + ')'

    @classmethod
    def lua_query(self, table):
        """Return the resulting objects as a list. Accepts a single dictionary-
        like object as an argument."""
        return self.query(**table).all()

    @classmethod
    def count(cls):
        return Session.query(cls).count()

    @classmethod
    def query(cls, *args, **kwargs):
        """Perform a query against this class."""
        return Session.query(cls).filter(*args).filter_by(**kwargs)

    @classmethod
    def first(cls):
        return cls.query().first()

    @classmethod
    def join(cls, *args, **kwargs):
        """Return a query object with a join."""
        return Session.query(cls).join(*args, **kwargs)

    @classmethod
    def get(cls, id):
        """Return a row with the exact id."""
        return Session.query(cls).get(id)


Base = declarative_base(bind=engine, cls=_Base)


class NameMixin:
    name = Column(String(50), nullable=False)

    def __str__(self):
        return f'{self.name} (#{self.id})'


class DescriptionMixin:
    _description = Column(String(500), nullable=True)

    @property
    def description(self):
        return self._description or 'You see nothing special.'

    @description.setter
    def description(self, value):
        self._description = value or None


class NameDescriptionMixin(NameMixin, DescriptionMixin):
    pass


class LocationMixin:
    @declared_attr
    def location_id(cls):
        return Column(Integer, ForeignKey('rooms.id'), nullable=True)

    @declared_attr
    def location(cls):
        return relationship(
            'Room', backref=cls.__tablename__, foreign_keys=[cls.location_id]
        )


class PasswordMixin:
    """Add passwords to things."""
    password = Column(String(80), nullable=True)

    @property
    def reset_password(self):
        return ''

    @reset_password.setter
    def reset_password(self, value):
        if value:  # Don't clear passwords.
            self.set_password(value)

    def check_password(self, secret):
        """Check that secret matches self.password."""
        return self.password is not None and crypt.verify(
            secret, self.password
        )

    def set_password(self, value):
        """Set self.password."""
        self.password = crypt.encrypt(value, rounds=10000)

    def clear_password(self):
        """Effectively lock the account."""
        self.password = None

    def randomise_password(self):
        """Set a random password for this character."""
        pwd = random_password()
        self.set_password(pwd)
        return pwd


class ExperienceMixin:
    experience = Column(Integer, nullable=False, default=0)


class LevelMixin:
    level = Column(Integer, nullable=False, default=0)


class StatisticsMixin:
    max_hitpoints = Column(Integer, nullable=False, default=0)
    max_mana = Column(Integer, nullable=False, default=0)
    max_endurance = Column(Integer, nullable=False, default=0)
    damage = Column(Integer, nullable=False, default=0)
    avoid = Column(Integer, nullable=False, default=0)
    constitution = Column(Integer, nullable=False, default=0)
    charisma = Column(Integer, nullable=False, default=0)
    divinity = Column(Integer, nullable=False, default=0)
    magic = Column(Integer, nullable=False, default=0)


class InvisibleMixin:
    invisible = Column(Boolean, nullable=False, default=False)


class CoordinatesMixin:
    x = Column(Integer, nullable=False, default=0.0)
    y = Column(Integer, nullable=False, default=0.0)
    z = Column(Integer, nullable=False, default=0.0)

    @property
    def coordinates(self):
        return (self.x, self.y, self.z)

    @coordinates.setter
    def coordinates(self, value):
        self.x, self.y, self.z = value


class CodeMixin:
    """Add code to anything."""

    code = Column(String(1000000), nullable=False)
