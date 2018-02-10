"""Building commands."""

from .base import Command
from db import Gender, Character, Room, Exit, Session as s


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
            r = Room(
                name=title, x=x, y=y, z=z, zone_id=character.location.zone_id
            )
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


class ZEdit(Command):
    """Edit the current zone."""

    def on_init(self):
        self.admin = True
        self.aliases.append('@zedit')
        self.add_argument('-n', '--name', help='New name for the zone')
        self.add_argument(
            '-d', '--description', help='New description for the zone'
        )
        self.add_argument(
            '-b', '--builder', help='Change ownership of the zone'
        )

    def func(self, character, args, text):
        z = character.location.zone
        for name in ('name', 'description'):
            value = getattr(args, name)
            if value:
                setattr(z, name, value)
            character.notify(f'{name.title()}: {getattr(z, name)}')
        if args.builder:
            obj = character.get_single_match(args.builder)
            if obj is not None:
                if isinstance(obj, Character):
                    z.builder = obj
                else:
                    self.exit(message=f'{obj} is not a character.')
        character.notify(f'Builder: {z.builder}.')


class REdit(Command):
    """Edit the current room."""

    def on_init(self):
        self.aliases.append('@redit')
        self.builder = True
        self.add_argument('-n', '--name', help='New name for the room')
        self.add_argument(
            '-d', '--description', help='New description for the room'
        )
        for name in ('x', 'y', 'z'):
            self.add_argument(
                f'-{name}', type=int,
                help=f'New {name} coordinate for the room'
            )
        for name in ('lit', 'safe', 'regain'):
            self.add_argument(
                f'--{name}', type=int, help=f'New {name} value for this room'
            )

    def func(self, character, args, text):
        for name in (
            'name', 'description', 'x', 'y', 'z', 'lit', 'safe', 'regain'
        ):
            value = getattr(args, name)
            if value or (name in ('lit', 'safe') and value is not None):
                if name in ('lit', 'safe'):
                    value = bool(value)
                setattr(character.location, name, value)
            character.notify(
                f'{name.title()}: {getattr(character.location, name)}'
            )


class Add_Gender(Command):
    """Add a gender."""

    def on_init(self):
        self.builder = True
        self.add_argument('name', help='The name for the new gender')
        # Skip name since we use it explicitly:
        self.valid_attribute_names = []
        pronouns = (
            ('subjective', 'he, she, or it'),
            ('objective', 'him, her, or it'),
            ('possessive_adjective', 'his, her, or its'),
            ('possessive_noun', 'his, hers, or its'),
            ('reflexive', 'himself, herself, or itself')
        )
        for name, description in pronouns:
            self.valid_attribute_names.append(name)
            self.add_argument(
                name, help=f'{self.get_readable_name(name)}: {description}'
            )

    def func(self, character, args, text):
        g = Gender(name=args.name)
        character.notify(f'Creating gender: {g.name}.')
        for name in self.valid_attribute_names:
            setattr(g, name, getattr(args, name))
            character.notify(
                f'{self.get_readable_name(name)}: {getattr(g, name)}'
            )
        s.add(g)

    def get_readable_name(self, name):
        """Return the readable form of name."""
        return name.replace('_', ' ').title()
