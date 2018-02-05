"""Social commands: say, emote."""


from .base import Command


class Say(Command):
    """Say something to everyone else in the room"""

    def __init__(self):
        super().__init__()
        self.add_argument('what', nargs='*', help='What to say')

    def func(self, connection, args):
        if not args.what:
            connection.notify('You say nothing.')
        else:
            connection.notify('You say: %s' % args.what)
