"""Provides the Character class."""

from sqlalchemy import Column, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from .base import (
    Base, NameDescriptionMixin, PasswordMixin, ExperienceMixin, LevelMixin,
    LocationMixin, StatisticsMixin, InvisibleMixin
)
from socials import socials
from util import english_list

connections = {}


class AmbiguousMatchError(Exception):
    """Multiple matches were found."""


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


class CharacterClassSecondary(Base):
    """Link characters to classes."""

    __tablename__ = 'character_class_secondary'
    character_id = Column(Integer, ForeignKey('characters.id'), nullable=False)
    character_class_id = Column(
        Integer, ForeignKey('character_classes.id'), nullable=False
    )


class Character(
    Base, NameDescriptionMixin, PasswordMixin, ExperienceMixin, LevelMixin,
    LocationMixin, StatisticsMixin, InvisibleMixin
):
    """A player instance."""

    __tablename__ = 'characters'
    gender_id = Column(Integer, ForeignKey('genders.id'), nullable=True)
    gender = relationship('Gender', backref='objects')
    connected = Column(Boolean, nullable=False, default=False)
    builder = Column(Boolean, nullable=False, default=False)
    admin = Column(Boolean, nullable=False, default=False)
    mobile = Column(Boolean, nullable=False, default=False)
    hitpoints = Column(Integer, nullable=True)
    mana = Column(Integer, nullable=True)
    endurance = Column(Integer, nullable=True)
    character_classes = relationship(
        'CharacterClass', backref='characters',
        secondary=CharacterClassSecondary.__table__
    )

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
            self.connection.object = None
            self.connection.transport.loseConnection()
        connections[self.id] = connection
        self.notify(f'Welcome back, {self.name}.')

    def get_gender(self):
        if self.gender_id is None:
            gid = 1
        else:
            gid = self.gender_id
        return Base._decl_class_registry['Gender'].get(gid)

    def notify(self, string):
        """Send a string of text to this character."""
        if self.connection is not None:
            return self.connection.notify(string)

    def show_location(self):
        """Show this character where they are."""
        self.notify(self.location.name)
        self.notify(self.location.description)
        if not self.location.exits:
            self.notify('You see no obvious exits.')
        else:
            exits = english_list(
                self.location.exits, key=lambda exit: exit.name, and_='or '
            )
            self.notify(f'You can go {exits}.')

    def do_social(self, string, _others=None, **kwargs):
        """Get social strings and send them out to players within this room.
        This object will be the first object in the perspectives list, that
        list will be extended by _others."""
        perspectives = [self]
        if _others is not None:
            perspectives.extend(_others)
        strings = socials.get_strings(string, perspectives, **kwargs)
        for obj in self.get_visible():
            if obj in perspectives:
                msg = strings[perspectives.index(obj)]
            else:
                msg = strings[-1]
            obj.notify(msg)

    def get_visible(self):
        """Get the things this player can see."""
        return [x for x in self.location.contents if not x.invisible]

    def match(self, string):
        """Match a string with an object from this room."""
        if self.admin and string.startswith('#'):
            return self.match_id(string[1:])
        else:
            return self.match_name(string.lower())

    def match_id(self, id):
        """Match on object ids."""
        return [x for x in self.get_visible() if str(x.id) == id]

    def match_name(self, name):
        """Matches on names."""
        if name == 'me':
            return [self]
        elif name == 'here':
            return [self.location]
        else:
            return [
                x for x in self.get_visible() if x.name.lower().startswith(
                    name
                )
            ]

    def match_single(self, string):
        """Return only a single match. Raise AmbiguousMatchError if more than
        one match is found."""
        results = self.match(string)
        if not results:
            return  # Let convert_emote_string handle it.
        elif len(results) == 1:
            return results[0]
        else:
            raise AmbiguousMatchError(string)


for name in ('hitpoints', 'mana', 'endurance'):
    setattr(Character, name[0], StatProperty(name))
