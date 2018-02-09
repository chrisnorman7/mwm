"""Social commands: say, emote."""


from socials import socials
from .base import Command


class Say(Command):
    """Say something to everyone else in the room"""

    def on_init(self):
        self.add_argument('text', nargs='*', help='What to say')

    def func(self, character, args, text):
        if not text:
            character.notify('You say nothing.')
        else:
            character.do_social('%1n say%1s: "{text}"', text=text)


class Emote(Command):
    """Emote something."""

    def on_init(self):
        self.add_argument('string', nargs='+', help='The string to emote')

    def func(self, character, args, text):
        string, perspectives = socials.convert_emote_string(
            f'%1n|normal {text}', character.match_single, [character]
        )
        perspectives.remove(character)
        character.do_social(string, _others=perspectives)
