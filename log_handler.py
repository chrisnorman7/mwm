"""Provides the LogHandler class."""

from logging import Handler
from db import Character


class LogHandler(Handler):
    """Log messages inside the game."""

    def emit(self, record):
        """Send the record in game."""
        msg = f'[{record.levelname}] {record.name}: {record.getMessage()}'
        for c in Character.query(admin=True, connected=True):
            c.notify(msg)
