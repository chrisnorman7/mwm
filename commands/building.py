"""Building commands."""

from .base import Command
from db import Room, Exit, session
from .movement import directions as _directions

directions = {y: x for x, y in _directions.items()}
reverse_directions = {
    'north': 'south',
    'northeast': 'southwest',
    'east': 'west',
    'southeast': 'northwest',
    'south': 'north',
    'southwest': 'northeast',
    'west': 'east',
    'northwest': 'southeast',
    'up': 'down',
    'down': 'up'
}


class Dig(Command):
    """Dig in the given direction to another room."""

    def on_init(self):
        self.aliases.append('@dig')
        self.builder = True
        self.add_argument(
            'direction', choices=directions.keys(),
            help='The direction to build in'
        )
        self.add_argument(
            'name', nargs='?', default='New Room',
            help='The name of the new room'
        )

    def func(self, character, args):
        if not args.name:
            self.exit(message='Room names cannot be blank.')
        direction = directions[args.direction]
        with session() as s:
            if Exit.query(
                name=direction, location_id=character.location_id
            ).count():
                self.exit(
                    message='There is already an exit in that direction.'
                )
            r = Room(name=args.name)
            s.add(r)
            s.commit()
            x = Exit(
                name=direction, location_id=character.location_id,
                target_id=r.id
            )
            y = Exit(
                name=reverse_directions[direction], location_id=r.id,
                target_id=character.location.id
            )
            s.add_all([x, y])
            s.commit()
            character.notify(f'Created room {r}.')
            for thing in [x, y]:
                character.notify(
                    f'Created exit {thing} from {thing.location} to '
                    f'{thing.target}.'
                )
