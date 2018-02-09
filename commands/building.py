"""Building commands."""

from .base import Command
from db import Room, Exit, session


class Dig(Command):
    """Dig in the given direction to another room."""

    def on_init(self):
        self.aliases.append('@dig')
        self.builder = True
        self.add_argument(
            'direction', help='The direction to build in'
        )
        self.add_argument(
            'title', nargs='?', default='New Room',
            help='The title of the new room'
        )

    def func(self, character, args, text):
        direction = args.direction
        title = args.title
        if not title:
            self.exit(message='Room titles cannot be blank.')
        with session() as s:
            d = character.location.match_direction(direction)
            if d is None:
                self.exit(message=f'Invalid exit: {direction}')
            direction = d.name
            if Exit.query(
                name=direction, location_id=character.location_id
            ).count():
                self.exit(
                    message='There is already an exit in that direction.'
                )
            x, y, z = d.coordinates_from(character.location.coordinates)
            r = Room.query(x=x, y=y, z=z).first()
            if r is None:
                r = Room(name=title, x=x, y=y, z=z)
                s.add(r)
                s.commit()
                msg = f'Created room {r}.'
            else:
                msg = f'Linking to room {r}.'
            character.notify(msg)
            x = Exit(
                name=direction, location_id=character.location_id,
                target_id=r.id
            )
            y = Exit(
                name=d.opposite.name, location_id=r.id,
                target_id=character.location.id
            )
            s.add_all([x, y])
            s.commit()
            for thing in [x, y]:
                character.notify(
                    f'Created exit {thing} from {thing.location} to '
                    f'{thing.target}.'
                )
