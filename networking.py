"""Provides the Protocol class for communicating with clients."""

import logging
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver
from db import Character
from config import config


class Protocol(LineReceiver):
    def connectionMade(self):
        self.object_id = None
        peer = self.transport.getPeer()
        self.host = peer.host
        self.port = peer.port
        self.logger = logging.getLogger('%s:%d' % (self.host, self.port))
        self.logger.info('Connected.')
        self.factory.connections.append(self)
        self.username = None
        self.notify(config.motd)

    def connectionLost(self, reason):
        self.logger.info(reason.getErrorMessage())
        self.factory.connections.remove(self)

    @property
    def object(self):
        if self.object_id is not None:
            return Character.get(self.object_id)

    @object.setter
    def object(self, character):
        if character is None:
            self.object_id = None
            return
        self.object_id = character.id
        character.connection = self

    def notify(self, string):
        """Send a string of text to this connection."""
        self.sendLine(string.encode())


class Factory(ServerFactory):
    """Store all connections."""

    protocol = Protocol

    def __init__(self):
        self.connections = []


factory = Factory()
