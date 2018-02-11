"""DB imports."""

import logging
import os
from inspect import isclass
from sqlalchemy import inspect
from yaml import load, dump
from pyperclip import copy, PyperclipException
from db_dumper import load as dumper_load, dump as dumper_dump
from config import config

# Database-specific stuff:
from .session import Session, session
from .rooms import Room, Direction, Exit, Zone, RoomCommand
from .guilds import Guild, GuildSecondary
from .genders import Gender
from .characters import Character, Race
from .objects import Object
from .base import Base, MatchError, single_match
from .skills import WeaponSkill, WeaponSkillSecondary, Spell, SpellSecondary


logger = logging.getLogger(__name__)

__all__ = [
    'Room', 'Character', 'Session', 'session', 'Base', 'Exit', 'Object',
    'dump_db', 'load_db', 'get_classes',  'Guild', 'GuildSecondary',
    'WeaponSkill', 'WeaponSkillSecondary', 'Spell', 'SpellSecondary', 'Gender',
    'Direction', 'Zone', 'Race', 'RoomCommand', 'MatchError', 'single_match'
]

Base.metadata.create_all()


def get_classes():
    """Returns a list of all classes used in the database."""
    classes = []
    for cls in Base._decl_class_registry.values():
        if isclass(cls) and issubclass(cls, Base):
            classes.append(cls)
    return classes


def dump_object(obj):
    """Return object obj as a dictionary."""
    columns = inspect(obj.__class__).columns
    d = {}
    for name, column in columns.items():
        value = getattr(obj, name)
        if (
            column.nullable is True and value is None
        ) or (
            column.default is not None and value == column.default.arg
        ):
            continue
        d[name] = value
    return d


def dump_db(where=None):
    """Dump the database to single files."""
    if where is None:
        where = config.db_file
    logger.info('Dumping the database to %s.', where)
    objects = []
    for cls in get_classes():
        objects.extend(Session.query(cls))
    y = dumper_dump(objects, dump_object)
    with open(where, 'w') as f:
        dump(y, stream=f)
    return len(objects)


def load_db():
    """Load the database from a single flat file."""
    logger.info('Creating database tables...')
    Base.metadata.create_all()
    if os.path.isfile(config.db_file):
        logger.info('Loading the database from %s.', config.db_file)
        with open(config.db_file, 'r') as f:
            y = load(f)
        with session() as s:
            objects = dumper_load(y, get_classes())
            s.add_all(objects)
    else:
        logger.info('Starting with blank database.')
    finalise_db()


def finalise_db():
    """Bootstrap an empty database."""
    with session() as s:
        for cls in get_classes():
            logger.info(
                '%s: %d', cls.__table__.name.replace('_', ' '), cls.count()
            )
        if not Direction.count():
            Direction.create(
                'north', x=0, y=1, z=0, opposite_string='the south'
            )
            Direction.create('east', x=1, opposite_string='the west')
            Direction.create('south', y=-1, opposite_string='the north')
            Direction.create('west', x=-1, opposite_string='the east')
            Direction.create('up', z=1, opposite_string='below')
            Direction.create('down', z=-1, opposite_string='above')
            Direction.create(
                'northeast', short_name='ne', x=1, y=1,
                opposite_string='the southwest'
            )
            Direction.create(
                'southeast', short_name='se', x=1, y=-1,
                opposite_string='the northwest'
            )
            Direction.create(
                'southwest', short_name='sw', x=-1, y=-1,
                opposite_string='the northeast'
            )
            Direction.create(
                'northwest', short_name='nw', x=-1, y=1,
                opposite_string='the southeast'
            )
            s.commit()
            for d in Direction.query():
                d.opposite = s.query(Direction).filter_by(
                    x=d.x * -1,
                    y=d.y * -1,
                    z=d.z * -1
                ).first()
                s.add(d)
                s.commit()
        if not Zone.count():
            s.add(Zone(name='Default Zone'))
        if not Room.count():
            s.add(Room(name='The First Room', zone_id=Zone.first().id))
            s.commit()
        if not Gender.count():
            s.add(Gender(name='Neutral'))
        if not Character.count():
            r = Room.first()
            c = Character(
                programmer=True, builder=True, admin=True, name='Wizard',
                location_id=r.id
            )
            password = c.randomise_password()
            logger.info(
                'Created default character "%s" with password %s.', c.name,
                password
            )
            try:
                copy(password)
                logger.info('Password copied to clipboard.')
            except PyperclipException:
                logger.info('Could not copy password to the clipboard.')
            s.add(c)
