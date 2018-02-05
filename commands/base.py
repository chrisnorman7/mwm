import logging
from shlex import split
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

logger = logging.getLogger(__name__)


class Command(ArgumentParser):
    """Overwrite stupid methods."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('prog', self.__class__.__name__.lower())
        kwargs.setdefault('formatter_class', ArgumentDefaultsHelpFormatter)
        kwargs.setdefault('description', self.__doc__)
        super().__init__(*args, **kwargs)
        self.aliases = []
        self.rest = None
        self.character = None

    def exit(self, status=0, message=None):
        """Don't exit the program."""
        if message:
            self._print_message(message)
        logger.info(
            'Command %s exited with status %s: %s', self.prog, status,
            message
        )

    def _print_message(self, message, file=None):
        if self.character is not None:
            self.character.notify(message)

    def run(self, character, rest):
        """Call with a Character instance and the text from the command line with the
        command name excluded."""
        self.rest = rest
        try:
            args = self.parse_args(split(self.rest, posix=False))
            self.character = character
            self.func(character, args)
        except Exception as e:
            logger.warning('Error in %r:', self)
            logger.exception(e)
            raise
        finally:
            self.character = None
            self.rest = None

    def func(self, character, args):
        """Override to provide a meaningful command."""
        raise NotImplementedError()
