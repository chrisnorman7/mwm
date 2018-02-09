"""Provides the Command class."""

import logging
import sys
from contextlib import redirect_stdout, redirect_stderr
from io import StringIO
from shlex import split
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

logger = logging.getLogger(__name__)


class CommandExit(Exception):
    """A command exited for some reason."""


class Command(ArgumentParser):
    """Overwrite stupid methods."""

    def __init__(self, *args, **kwargs):
        kwargs.setdefault(
            'prog', self.__class__.__name__.lower().replace('_', '-')
        )
        kwargs.setdefault('formatter_class', ArgumentDefaultsHelpFormatter)
        kwargs.setdefault('description', self.__doc__)
        super().__init__(*args, **kwargs)
        self.builder = False
        self.admin = False
        self.aliases = []
        self.on_init()

    def on_init(self):
        """Called after __init__, avoiding all that super rubbish."""

    def _print_message(self, message, file=None):
        """Always print to sys.stdout."""
        sys.stdout.write(message)

    def exit(self, status=0, message=None):
        """Don't exit the program."""
        if message:
            sys.stdout.write(message)
        raise CommandExit()

    def run(self, character, text):
        """Call with a Character instance and the text from the command line with the
        command name excluded."""
        f = StringIO()
        with redirect_stdout(f), redirect_stderr(f):
            try:
                cmd = split(text)
            except ValueError:  # Probably unbalanced quotation marks.
                cmd = text
            try:
                args = self.parse_args(cmd)
                self.func(character, args, text)
            except CommandExit:
                pass  # That's OK.
            except Exception as e:
                logger.warning('Error in %r:', self)
                logger.exception(e)
                raise
            finally:
                f.seek(0)
                character.notify(f.read())

    def func(self, character, args, text):
        """Override to provide a meaningful command."""
        raise NotImplementedError()

    def allowed(self, character):
        """Returns True if character is allowed to use this command, False
        otherwise."""
        for perm in ('admin', 'builder'):
            if getattr(self, perm) > getattr(character, perm):
                return False
        return True
