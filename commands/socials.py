"""Social commands: say, emote."""


from .base import Command


class Say(Command):
    """Say something to everyone else in the room"""

    def on_init(self):
        self.add_argument('text', nargs='*', help='What to say')

    def func(self, character, args):
        if not self.rest:
            character.notify('You say nothing.')
        else:
            character.do_social('%1n say%1s: "{text}"', text=self.rest)
