"""Miscelaneous commands."""

import logging
from twisted.internet import reactor
import networking
from util import pluralise, english_list
from .base import Command

logger = logging.getLogger(__name__)


class Quit(Command):
    """Disconnect from the game."""

    def on_init(self):
        self.aliases.append('@quit')

    def func(self, character, args):
        """Let's disconnect them."""
        if self.rest:
            character.notify('This command takes no arguments.')
        else:
            character.notify('See you soon.')
            character.connection.transport.loseConnection()


class Password(Command):
    """Change your password."""

    def on_init(self):
        self.aliases.append('@password')
        self.add_argument('old', help='Your old password')
        self.add_argument('new', help='Your new password')

    def func(self, character, args):
        if character.check_password(args.old):
            if args.new:
                character.set_password(args.new)
                if args.old != args.new:
                    character.notify('Password changed.')
                else:
                    character.notify('Password unchanged.')
            else:
                character.notify('Passwords cannot be blank.')
        else:
            character.notify('Incorrect password.')


class Inventory(Command):
    """Show what you are holding."""

    def on_init(self):
        self.aliases.extend(['i', 'inv', 'holding', 'h'])

    def func(self, character, args):
        """Show them what they're holding."""
        if not character.inventory:
            character.notify('You are holding nothing.')
        else:
            character.notify('You are holding:')
            for thing in character.inventory:
                character.notify(thing.name)


class Commands(Command):
    """Show all commands."""

    def on_init(self):
        self.aliases.append('@commands')

    def func(self, character, args):
        character.notify('Commands:')
        for cmd in sorted(
            set(networking.commands_table.values()),
            key=lambda c: c.prog
        ):
            if not cmd.allowed(character):
                continue
            character.notify(f'{cmd.prog}: {cmd.description}')
            character.notify(f'Aliases: {english_list(cmd.aliases)}.')


class Shutdown(Command):
    """Shutdown the server."""

    def on_init(self):
        self.admin = True
        self.aliases.append('@shutdown')
        self.add_argument(
            '-a', '--after', type=int, default=10,
            help='How long until the shutdown occurs'
        )
        self.add_argument(
            '-m', '--message', default='The server is shutting down.',
            help='The message to show to connected players'
        )

    def func(self, character, args):
        logger.info('Shutdown initiated by %s.', character.name)
        networking.factory.shutdown_task = reactor.callLater(
            args.after, reactor.stop
        )
        when = f'{args.after} {pluralise(args.after, "second")}'
        networking.factory.broadcast(f'*** Shutdown in {when}. ***')
        networking.factory.broadcast(args.message)


class Abort_Shutdown(Command):
    """Abort shutdown."""

    def on_init(self):
        self.aliases.extend(
            ['@abort-shutdown', '@abort-s', '@shutdown-abort', '@shutdown-a']
        )
        self.admin = True
        self.add_argument(
            '-m', '--message', help='The reason for aborting the shutdown'
        )

    def func(self, character, args):
        if networking.factory.shutdown_task is None:
            character.notify('The server is not shutting down.')
        else:
            logger.info('Shutdown aborted by %s.', character.name)
            networking.factory.shutdown_task.cancel()
            networking.factory.shutdown_task = None
            networking.factory.broadcast('*** Shutdown aborted. ***')
            if args.message is not None:
                networking.factory.broadcast(args.message)
