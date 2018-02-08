"""Provides room-related classes."""

import logging
from sqlalchemy import Column, Boolean, Integer, ForeignKey, String, or_
from sqlalchemy.orm import relationship
from .base import (
    Base, NameMixin, NameDescriptionMixin, LocationMixin, CoordinatesMixin
)
from .session import Session

logger = logging.getLogger(__name__)


class Direction(Base, NameMixin, CoordinatesMixin):
    """A direction a player or vehicle can move in."""

    __tablename__ = 'directions'
    short_name = Column(String(2), nullable=False)
    opposite_id = Column(
        Integer,
        ForeignKey(f'{__tablename__}.id'),
        nullable=True,  # Undesirable but prevents a chicken and egg situation.
        default=None
    )
    opposite = relationship(
        'Direction',
        backref='opposites',
        remote_side='Direction.id'
    )
    opposite_string = Column(String(50), nullable=False)

    def coordinates_from(self, start):
        """Apply this direction to coordinates start and return the
        destination coordinates."""
        x, y, z = start
        return (
            x + self.x,
            y + self.y,
            z + self.z
        )

    @classmethod
    def create(cls, name, **kwargs):
        kwargs.setdefault('short_name', name[0])
        d = cls(name=name, **kwargs)
        logger.info('Created direction %s.', d.name)
        Session.add(d)
        return d


class Zone(Base, NameDescriptionMixin):
    """A zone which contains 0 or more rooms."""

    __tablename__ = 'zones'
    builder_id = Column(Integer, ForeignKey('characters.id'), nullable=True)
    builder = relationship('Character', backref='zones')


class Room(Base, NameDescriptionMixin, CoordinatesMixin):
    """A room instance."""

    __tablename__ = 'rooms'
    lit = Column(Boolean, nullable=False, default=True)
    safe = Column(Boolean, nullable=False, default=False)
    regain = Column(Integer, nullable=False, default=1)
    zone_id = Column(Integer, ForeignKey('zones.id'), nullable=False)
    zone = relationship('Zone', backref='rooms')

    @property
    def contents(self):
        return self.objects + self.characters

    def broadcast(self, message):
        """Send a message to everyone in this room."""
        for c in self.characters:
            c.notify(message)

    def match_direction(self, string):
        """Return a single direction or None."""
        return Direction.query(
            or_(Direction.name == string, Direction.short_name == string)
        ).first()


class Exit(Base, NameDescriptionMixin, LocationMixin):
    """Link rooms together."""

    __tablename__ = 'exits'
    target_id = Column(Integer, ForeignKey('rooms.id'), nullable=True)
    target = relationship(
        'Room', backref='entrances', foreign_keys=[target_id]
    )
    use_msg = Column(
        String(150), nullable=False, default='%1n walk%1s %2n.'
    )
    arrive_msg = Column(
        String(150), nullable=False, default='%1n arrives from {direction}.'
    )
