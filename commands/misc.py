"""Miscelaneous commands."""

from .base import Command


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
