"""Movement commands."""

from .base import Command
from db import Exit, Direction
from socials import socials
from programming import manage_environment


class Go(Command):
    """Go in a specific direction."""

    def on_init(self):
        self.add_argument('direction', help='The direction to go in.')

    def func(self, character, args, rest):
        x = Exit.query(
            location_id=character.location_id, name=args.direction.lower()
        ).first()
        if x is None:
            self.exit(message='You cannot go that way.')
        if x.can_use is not None:
            with manage_environment(character=character) as lua:
                if not lua.execute(x.can_use):
                    return  # They cannot pass.
        character.do_social(x.use_msg, _others=[x])
        d = Direction.query(name=x.name).first()
        if d is None:
            msg = f'{character.name} arrives.'
        else:
            msg = socials.get_strings(
                x.arrive_msg, [character], direction=d.opposite_string
                )
        x.target.broadcast(msg)
        character.location = x.target
        character.show_location()
