"""Provides the Room class."""

from sqlalchemy import Column, Boolean, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from .base import Base, NameDescriptionMixin, LocationMixin


class Room(Base, NameDescriptionMixin):
    """A room instance."""

    __tablename__ = 'rooms'
    lit = Column(Boolean, nullable=False, default=True)
    safe = Column(Boolean, nullable=False, default=False)
    regain = Column(Integer, nullable=False, default=1)


class Door(Base, NameDescriptionMixin, LocationMixin):
    """Link rooms together."""

    __tablename__ = 'doors'
    target_id = Column(Integer, ForeignKey('rooms.id'), nullable=True)
    target = relationship(
        'Room', backref='entrances', foreign_keys=[target_id]
    )
    use_msg = Column(
        String(150), nullable=False, default='You walk through {}.'
    )
