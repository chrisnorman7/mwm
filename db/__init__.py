"""DB imports."""

import logging
import os
from inspect import isclass
from sqlalchemy import inspect
from yaml import load, dump
from db_dumper import load as dumper_load, dump as dumper_dump
from config import config


# Database-specific stuff:
from .session import Session, session
from .rooms import Room, Exit
from .guilds import Guild, GuildSecondary
from .genders import Gender
from .characters import Character
from .objects import Object
from .base import Base
from .skills import WeaponSkill, WeaponSkillSecondary, Spell, SpellSecondary


logger = logging.getLogger(__name__)

__all__ = [
    'Room', 'Character', 'Session', 'session', 'Base', 'Exit', 'Object',
    'dump_db', 'load_db', 'get_classes', 'CharacterClass',
    'Guild', 'GuildSecondary', 'WeaponSkill', 'WeaponSkillSecondary', 'Spell',
    'SpellSecondary', 'Gender'
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
        if not Room.count():
            s.add(Room(name='The First Room'))
            s.commit()
        if not Gender.count():
            s.add(Gender(name='Neutral'))
        if not Character.count():
            r = Room.first()
            c = Character(
                builder=True, admin=True, name='Wizard', location_id=r.id
            )
            password = c.randomise_password()
            logger.info(
                'Created default character "%s" with password %s.', c.name,
                password
            )
            s.add(c)
