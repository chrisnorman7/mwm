"""Boring database tests."""

from db import Room, Player, session, Door


with session() as s:
    r = Room(name='Test Room')
    p = Player(name='Test Player', location=r)
    s.add_all((p, r))
    s.commit()
    rid = r.id
    pid = p.id


def test_location_ids():
    p = Player.get(pid)
    assert p.location_id == rid


def test_stats():
    p = Player.get(pid)
    p.max_hitpoints = 50
    assert p.h == p.max_hitpoints
    p.h = 5
    assert p.h == 5
    assert p.max_hitpoints == 50
    p.h = p.max_hitpoints
    assert p.hitpoints is None


def test_door():
    with session() as s:
        d = Door(name='a small door', location_id=rid)
        s.add(d)
        s.commit()
        assert d.target is None
        assert d.use_msg.format(d.name) == 'You walk through a small door.'
