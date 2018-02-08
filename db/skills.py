"""Provides skil-related classes."""

from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from .base import Base, NameDescriptionMixin, LevelMixin


class SkillMixin:
    max_level = Column(Integer, nullable=False, default=100)

    @declared_attr
    def characters(cls):
        return relationship(
            'Character', backref=cls.__backref_skill_name__,
            secondary=cls.__backref_skill_table__
        )


class ActiveSkillMixin(SkillMixin):
    endurance = Column(Integer, nullable=False, default=0)
    mana = Column(Integer, nullable=False, default=0)
    hitpoints = Column(Integer, nullable=False, default=0)
    damage = Column(Integer, nullable=False, default=0)
    use_msg = Column(
        String(100), nullable=False, default='%1n use%1s an untitled skill.'
    )
    on_use = Column(
        String(10000), nullable=False,
        default='character.notify("This skill has not been programmed.")'
    )


class SkillSecondaryMixin(LevelMixin):
    """Link skills to players."""

    @declared_attr
    def character_id(cls):
        return Column(Integer, ForeignKey('characters.id'), nullable=False)

    @declared_attr
    def skill_id(cls):
        return Column(
            Integer, ForeignKey(f'{cls.__skill_table_name__}.id'),
            nullable=False
        )


class WeaponSkillSecondary(Base, SkillSecondaryMixin):
    """Link weapon skills to characters."""

    __tablename__ = 'weapon_skill_secondary'
    __skill_table_name__ = 'weapon_skills'


class WeaponSkill(Base, NameDescriptionMixin, SkillMixin):
    """Weapon skills."""

    __tablename__ = 'weapon_skills'
    __backref_skill_name__ = 'weapon_skills'
    __backref_skill_table__ = WeaponSkillSecondary.__table__


class SpellSecondary(Base, SkillSecondaryMixin):
    """Link spells to characters."""

    __tablename__ = 'spell_secondary'
    __skill_table_name__ = 'spells'


class Spell(Base, NameDescriptionMixin, ActiveSkillMixin):
    """A magical or divine spell."""

    __tablename__ = 'spells'
    __backref_skill_name__ = 'spells'
    __backref_skill_table__ = SpellSecondary.__table__
    min_divinity = Column(Integer, nullable=False, default=0)
    min_magic = Column(Integer, nullable=False, default=0)
