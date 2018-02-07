"""Provides the Room class."""

from sqlalchemy import Column, Boolean, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from .base import Base, NameDescriptionMixin, LocationMixin

reverse_exits = {
    'north': 'the south',
    'northeast': 'the southwest',
    'east': 'the west',
    'southeast': 'the northwest',
    'south': 'the north',
    'southwest': 'the northeast',
    'west': 'the east',
    'northwest': 'the southeast',
    'up': 'below',
    'down': 'above'
}


class Room(Base, NameDescriptionMixin):
    """A room instance."""

    __tablename__ = 'rooms'
    lit = Column(Boolean, nullable=False, default=True)
    safe = Column(Boolean, nullable=False, default=False)
    regain = Column(Integer, nullable=False, default=1)
    arrive_msg = Column(String(150), nullable=False, default='%1n arrives.')

    @property
    def contents(self):
        return self.objects + self.characters


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
