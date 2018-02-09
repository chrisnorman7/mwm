"""Administrative commands."""

import logging
from lupa import LuaRuntime
from commands.base import Command

lua = LuaRuntime()
logger = logging.getLogger(__name__)


class Eval(Command):
    """Run some lua code."""

    def on_init(self):
        self.add_argument('code', nargs='+', help='The code to run')
        self.aliases.append('@eval')

    def func(self, character, args, text):
        code = f'function (character)\nreturn {text}\nend'
        try:
            character.notify(str(lua.eval(code)(character)))
        except Exception as e:
            self.exit(str(e))
            logger.exception(e)
