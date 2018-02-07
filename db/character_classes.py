"""Provides the CharacterClass class."""

from .base import Base, NameDescriptionMixin


class CharacterClass(Base, NameDescriptionMixin):
    """A class for characters."""

    __tablename__ = 'character_classes'
