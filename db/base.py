"""Provides base classes and mixins."""

from passlib.hash import sha256_crypt as crypt
from sqlalchemy import Column, Integer, String, ForeignKey, inspect
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from .engine import engine


class _Base:
    """The base class for declarative."""

    id = Column(Integer, primary_key=True)

    def __repr__(self):
        res = f'{self.__class__.__name__} ('
        strings = []
        for name in inspect(self.__class__).columns.keys():
            strings.append(f'{name}={getattr(self, name)}')
        return res + ', '.join(strings) + ')'


Base = declarative_base(bind=engine, cls=_Base)


class NameMixin:
    name = Column(String(50), nullable=False)


class DescriptionMixin:
    _description = Column(String(500), nullable=True)

    @property
    def description(self):
        return self._description or 'You see nothing special.'

    @description.setter
    def description(self, value):
        self._description = value or None


class LocationMixin:
    @declared_attr
    def location_id(cls):
        return Column(Integer, ForeignKey('rooms.id'), nullable=False)

    @declared_attr
    def location(cls):
        return relationship('Room', backref=cls.__tablename__)


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


class ExperienceMixin:
    experience = Column(Integer, nullable=False, default=0)


class LevelMixin:
    level = Column(Integer, nullable=False, default=0)


class StatisticsMixin:
    max_hitpoints = Column(Integer, nullable=False, default=0)
    max_mana = Column(Integer, nullable=False, default=0)
    max_endurance = Column(Integer, nullable=False, default=0)
    strength = Column(Integer, nullable=False, default=0)
    dexterity = Column(Integer, nullable=False, default=0)
    constitution = Column(Integer, nullable=False, default=0)
    charisma = Column(Integer, nullable=False, default=0)
    wisdom = Column(Integer, nullable=False, default=0)
    divinity = Column(Integer, nullable=False, default=0)
    magic = Column(Integer, nullable=False, default=0)
