"""Movement commands."""

import networking
from .base import Command
from db import Exit, session
from db.rooms import reverse_exits
from socials import socials
directions = {
    'north': 'n',
    'northeast': 'ne',
    'east': 'e',
    'southeast': 'se',
    'south': 's',
    'southwest': 'sw',
    'west': 'w',
    'northwest': 'nw',
    'up': 'u',
    'down': 'd'
}


class Go(Command):
    """Go in a specific direction."""

    def on_init(self):
        self.add_argument('direction', help='The direction to go in.')
        for long, short in directions.items():
            d = Direction(prog=long, description=f'Go {long}.')
            d.aliases.append(short)
            for part in (long, short):
                networking.commands_table[part] = d

    def func(self, character, args):
        with session() as s:
            x = Exit.query(
                location_id=character.location_id, name=args.direction.lower()
            ).first()
            if x is None:
                return character.notify('You cannot go that way.')
            character.do_social(x.use_msg, _others=[x])
            if x.name in reverse_exits:
                direction = reverse_exits[x.name]
                msg = socials.get_strings(
                    x.arrive_msg, [character], direction=direction
                    )
            else:
                msg = f'{character.name} arrives.'
            x.target.broadcast(msg)
            s.add(character)
            character.location = x.target
            character.show_location()


class Direction(Command):
    """Move in the given direction."""

    def func(self, character, args):
        networking.commands_table['go'].run(character, self.prog)
