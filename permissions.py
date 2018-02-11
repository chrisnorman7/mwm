"""Contains functions for checking character permissions. The functions raise
MatchError if they are not happy."""

import db


def check_privileges(character, *names):
    """Check all members of names. If getattr(character, name) evaluates to
    False raise CommandExit."""
    for name in names:
        if not getattr(character, name):
            raise db.MatchError(f'You do not have {name} privileges.')


def check_builder(character):
    return check_privileges(character, 'builder')


def check_admin(character):
    return check_privileges(character, 'admin')


def check_programmer(character):
    return check_privileges(character, 'programmer')
