"""Miscelaneous commands."""

from .base import Command


class Quit(Command):
    """Disconnect from the game."""

    def __init__(self):
        super().__init__()
        self.aliases.append('@quit')

    def func(self, character, rest):
        """Let's disconnect them."""
        print(self.rest)
        if self.rest:
            character.notify('This command takes no arguments.')
        else:
            character.notify('See you soon.')
            character.connection.transport.loseConnection()
