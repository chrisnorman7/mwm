"""Contains functions for checking character permissions. The functions raise
MatchError if they are not happy."""

from attr import attrs, attrib
from db import MatchError


def check_privileges(character, *names):
    """Check all members of names. If getattr(character, name) evaluates to
    False raise CommandExit."""
    for name in names:
        if not getattr(character, name):
            raise MatchError(f'You do not have {name} privileges.')


@attrs
class SimpleChecker:
    """Check privileges without lots of retyping."""

    name = attrib()

    def __call__(self, character):
        return check_privileges(character, self.name)


check_builder = SimpleChecker('builder')
check_admin = SimpleChecker('admin')
check_programmer = SimpleChecker('programmer')
