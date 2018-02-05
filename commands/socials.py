"""Social commands: say, emote."""


from .base import Command


class Say(Command):
    """Say something to everyone else in the room"""

    def __init__(self):
        super().__init__()
        self.add_argument('what', nargs='*', help='What to say')

    def func(self, character, args):
        if not args.what:
            character.notify('You say nothing.')
        else:
            character.do_social('%1n say%1s: "{text}"', text=self.rest)
