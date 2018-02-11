"""Administrative commands."""

import logging
from programming import manage_environment, as_function
from intercepts import Intercept
from db import Character, Room, RoomCommand, Session as s
from config import config
from .base import Command, CommandExit

logger = logging.getLogger(__name__)


def get_programmer(character_id):
    """Ensure the given character is a programmer. If they are return a
    Character instance. If not raise CommandExit."""
    character = Character.get(character_id)
    if character.programmer:
        return character
    character.notify('You have since been demoted.')
    raise CommandExit()


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
        character.notify('<code>')
        character.notify(cmd.code)
        character.notify('</code>')

    def func(self, character, args, text):
        cmd = self.get_command(character.location_id, args.name)
        i = Intercept(
            self.set_command_code, args=(
                args.name, args.description, character.location_id,
                character.id),
            multiline=True
        )
        character.notify('<code>')
        character.notify(cmd.code)
        character.notify('</code>')
        character.notify('Enter the new code:')
        character.connection.set_intercept(i)
