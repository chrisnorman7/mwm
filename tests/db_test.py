"""Boring database tests."""

from db import Room, Character, session, Exit, Object, Guild, GuildSecondary


with session() as s:
    r = Room(name='Test Room')
    c = Character(name='Test Player', location=r)
    s.add_all((c, r))
    s.commit()
    rid = r.id
    cid = c.id


def test_location_ids():
    c = Character.get(cid)
    assert c.location_id == rid


def test_stats():
    c = Character.get(cid)
    c.max_hitpoints = 50
    assert c.h == c.max_hitpoints
    c.h = 5
    assert c.h == 5
    assert c.max_hitpoints == 50
    c.h = c.max_hitpoints
    assert c.hitpoints is None


def test_Exit():
    with session() as s:
        d = Exit(name='a small Exit', location_id=rid)
        s.add(d)
        s.commit()
        assert d.target is None


def test_object():
    with session() as s:
        o = Object(name='Test Object')
        s.add(o)
        s.commit()
        assert o.inside is None
        assert o.parent is None


def test_container():
    with session() as s:
        c = Object(container=True, name='Test Container')
        s.add(c)
        s.commit()
        o = Object(inside_id=c.id, name='Test Object inside Something Else')
        s.add(o)
        s.commit()
        assert o.inside is c
        assert o in c.contains


def test_guilds():
    with session() as s:
        g1 = Guild(name='First Test Guild')
        g2 = Guild(name='Second Test Guild')
        s.add_all([g1, g2])
        s.commit()
        c = Character.get(cid)
        s1 = GuildSecondary(character_id=c.id, guild_id=g1.id)
        s2 = GuildSecondary(character_id=c.id, guild_id=g2.id)
        s.add_all([s1, s2])
        s.commit()
        assert g1 in c.guilds
        assert g2 in c.guilds
        assert len(c.guilds) == 2
        assert c.level == 0
        s1.level = 5
        s2.level = 10
        assert c.get_level() == 15
