"""Administrative commands."""

import logging
from programming import manage_environment, as_function
from intercepts import Intercept
from db import Character, Race, Room, RoomCommand, Session as s
from db.base import Base, Code, single_match
from config import config
from permissions import check_programmer
from .base import Command

logger = logging.getLogger(__name__)


def get_programmer(character_id):
    """Ensure the given character is a programmer. If they are return a
    Character instance. If not raise CommandExit."""
    character = Character.get(character_id)
    check_programmer(character)
    return character


class Eval(Command):
    """Eval Lua code."""

    def on_init(self):
        self.programmer = True
        self.add_argument('code', nargs='+', help='The code to run')
        self.aliases.append('@eval')

    def func(self, character, args, text):
        try:
            with manage_environment(
                character=character, here=character.location
            ) as lua:
                character.notify(repr(lua.eval(text)))
        except Exception as e:
            character.notify(str(e))
            logger.exception(e)


class Exec(Command):
    """Execute Lua code."""

    def on_init(self):
        self.programmer = True
        self.add_argument('code', nargs='+', help='The code to run')
        self.aliases.extend(['execute', '@exec', '@execute'])

    def func(self, character, args, text):
        try:
            character.notify(
                repr(
                    as_function(
                        text, character=character, here=character.location
                    )
                )
            )
        except Exception as e:
            character.notify(str(e))
            logger.exception(e)


class Room_Command(Command):
    """Add a command to this room."""

    def on_init(self):
        self.programmer = True
        self.add_argument('name', help='The name of the new command')
        self.add_argument(
            'description', help='The description of the new command'
        )

    def check_command_name(self, name, room):
        """Ensure there isn't a command with the given name on the given
        room. If there is, exit with a message."""
        if RoomCommand.query(name=name, location_id=room.id).count():
            return self.exit(
                message='There is already a command by that name in this room.'
            )

    def create_room_command(
        self, code, name, description, room_id, character_id
    ):
        """Create a room command. Used by the code-grabbing intercept."""
        character = get_programmer(character_id)
        self.check_command_name(name, Room.get(room_id))
        cmd = RoomCommand(
            name=name, code=code, _description=description, location_id=room_id
        )
        s.add(cmd)
        s.commit()
        character.notify(f'Created room command {cmd}.')

    def func(self, character, args, text):
        self.check_command_name(args.name, character.location)
        character.notify(f'Enter the code for the {args.name} command.')
        i = Intercept(
            self.create_room_command, multiline=True, args=(
                args.name, args.description, character.location_id,
                character.id
            )
        )
        character.connection.set_intercept(i)


class MOTD(Command):
    """Set the message of the day."""

    def on_init(self):
        self.admin = True

    def set_motd(self, text, character_id):
        """Set the MOTD."""
        char = Character.get(character_id)
        if not char.admin:
            return char.notify('You are not an admin.')
        config.motd = text
        char.notify('MOTD set.')

    def func(self, character, args, text):
        i = Intercept(self.set_motd, args=[character.id], multiline=True)
        character.notify('Enter the text of the motd.')
        character.connection.set_intercept(i)


class Edit_Room_Command(Command):
    """Edit an existing room command."""

    def on_init(self):
        self.programmer = True
        self.add_argument('name', help='The name of the existing room command')
        self.add_argument(
            'description', nargs='?',
            help='The new description for the command'
        )

    def get_command(self, room_id, name):
        """Get a valid command or raise CommandExit."""
        cmd = RoomCommand.query(location_id=room_id, name=name).first()
        if cmd is None:
            self.exit(
                message=f'There is no command named "{name}" on this room.'
            )
        return cmd

    def set_command_code(self, code, name, description, room_id, character_id):
        """Used by the intercept."""
        character = get_programmer(character_id)
        cmd = self.get_command(room_id, name)
        if description is not None:
            cmd.description = description
            character.notify(f'Description: {cmd.description}')
        cmd.code = code
        character.notify_code(cmd.code)

    def func(self, character, args, text):
        cmd = self.get_command(character.location_id, args.name)
        i = Intercept(
            self.set_command_code, args=(
                args.name, args.description, character.location_id,
                character.id),
            multiline=True
        )
        character.notify_code(cmd.code)
        character.notify('Enter the new code:')
        character.connection.set_intercept(i)


class Program(Command):
    """Program a property of something."""

    def on_init(self):
        self.aliases.append('@program')
        self.programmer = True
        self.add_argument('thing', help='thing.name')
        self.add_argument(
            '-n', '--null', action='store_true',
            help='Clear the code for this program'
        )

    def set_program_code(self, code, class_name, id, prop, character_id):
        """Used by the intercept."""
        character = get_programmer(character_id)
        if not code.strip():
            return character.notify('Blank code.')
        cls = Base._decl_class_registry[class_name]
        thing = cls.get(id)
        setattr(thing, prop, code)
        character.notify('Code set.')

    def func(self, character, args, text):
        split = args.thing.split('.')
        if len(split) != 2:
            self.exit(message=f'Invalid specifier "{args.thing}".')
        name, prop = split
        thing = single_match(name, character.match(name))
        if prop not in thing.__class__.__table__.c:
            self.exit(message=f'Invalid property name "{prop}".')
        col = thing.__class__.__table__.c[prop]
        if col.type.__class__ is not Code:
            self.exit(message=f'Property "{prop}" is not code.')
        character.notify_code(getattr(thing, prop) or '')
        if args.null:
            if col.nullable:
                setattr(thing, prop, None)
                character.notify('Code cleared.')
            else:
                self.exit('Code for this program is mandatory.')
        else:
            i = Intercept(
                self.set_program_code, multiline=True,
                args=(thing.__class__.__name__, thing.id, prop, character.id)
            )
            character.notify(f'You are programming "{prop}" of {thing}.')
            character.notify('Enter lines of code.')
            character.connection.set_intercept(i)


class Create_Race(Command):
    """Create a new race."""

    def on_init(self):
        self.admin = True
        self.add_argument('name', help='The name for the new race')
        self.add_argument(
            'description', help='The description for the new race'
        )

    def func(self, character, args, text):
        r = Race(
            name=args.name, _description=args.description,
            location_id=character.location_id
        )
        s.add(r)
        s.commit()
        character.notify(f'Created race {r}.')


class Set_Race_Home(Command):
    """Set this room to be the home for a particular race."""

    def on_init(self):
        self.admin = True
        self.add_argument('race', help='The race to set the home for')

    def func(self, character, args, text):
        r = Race.query(name=args.race).first()
        if r is None:
            self.exit(message=f'No race named "{args.race}" found.')
        r.location = character.location
        character.notify('Home set.')
