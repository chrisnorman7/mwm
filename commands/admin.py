"""Administrative commands."""

import logging
from programming import manage_environment
from commands.base import Command

logger = logging.getLogger(__name__)


class Eval(Command):
    """Eval Lua code."""

    def on_init(self):
        self.admin = True
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
        self.admin = True
        self.add_argument('code', nargs='+', help='The code to run')
        self.aliases.extend(['execute', '@exec', '@execute'])

    def func(self, character, args, text):
        try:
            with manage_environment(
                character=character, here=character.location
            ) as lua:
                lua.execute(text)
                character.notify('Done.')
        except Exception as e:
            character.notify(str(e))
            logger.exception(e)
