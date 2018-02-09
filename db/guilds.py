"""Provides the Guild class."""

from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base, NameDescriptionMixin, LevelMixin


class GuildSecondary(Base, LevelMixin):
    """Link characters to classes."""

    __tablename__ = 'guild_secondary'
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    guild_id = Column(
        Integer, ForeignKey('guilds.id'), nullable=False
    )


class Guild(Base, NameDescriptionMixin):
    """A class for characters."""

    __tablename__ = 'guilds'
    characters = relationship(
        'Character', backref='guilds', secondary=GuildSecondary.__table__
    )
