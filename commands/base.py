import logging
from shlex import split
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

logger = logging.getLogger(__name__)


class CommandExit(Exception):
    """Command exited for some reason."""

    def __init__(self, command, status, message):
        super().__init__(f'{status}: {message}')
        logger.info(
            'Command %s exited with status %s: %s', command, status, message
        )


class Command(ArgumentParser):
    """Overwrite stupid methods."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('prog', self.__class__.__name__.lower())
        kwargs.setdefault('formatter_class', ArgumentDefaultsHelpFormatter)
        kwargs.setdefault('description', self.__doc__)
        super().__init__(*args, **kwargs)

    def exit(self, status=0, message=None):
        """Don't exit the program."""
        if message:
            self._print_message(message)
        raise CommandExit(self, status, message)

    def _print_message(self, message, file=None):
        if self.connection is None:
            raise RuntimeError()
        self.connection.notify(message)

    def run(self, connection, rest):
        """Call with a connection and the text from the command line with the
        command name excluded."""
        rest = split(rest)
        try:
            args = self.parse_args(rest)
            self.connection = connection
            self.func(connection, args)
        except CommandExit:
            pass
        except Exception:
            logger.warning('Error in %r:', self)
            logger.exception()
            raise
        finally:
            self.connection = None

    def func(self, connection, args):
        """Override to provide a meaningful command."""
        raise NotImplementedError()
