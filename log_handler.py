"""Provides the LogHandler class."""

from logging import Handler
from twisted.internet import reactor
from db import Character


class LogHandler(Handler):
    """Log messages inside the game."""

    def emit(self, record):
        """Send the record in game."""
        msg = f'[{record.levelname}] {record.name}: {record.getMessage()}'
        reactor.callFromThread(self.send_message, msg)

    def send_message(self, msg):
        """Send msg to all connected admins."""
        for c in Character.query(admin=True, connected=True):
            c.notify(msg)
