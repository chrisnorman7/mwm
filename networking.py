"""Provides the Protocol class for communicating with clients."""

import logging
import sys
from inspect import isclass
from sqlalchemy import func
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver
import commands
from commands.base import Command
from db import Character, session
from config import config

encoding = sys.getdefaultencoding()
logger = logging.getLogger(__name__)

commands_table = {}

logger.info('Building commands table...')
for x in dir(commands):
    cls = getattr(commands, x)
    if isclass(cls) and issubclass(cls, Command):
        cmd = cls()
        for alias in set([cmd.prog] + cmd.aliases):
            alias = alias.lower().replace('_', '-')
            logger.debug('%s => %r.', alias, cmd)
            commands_table[alias] = cmd
logger.info('Commands loaded: %d.', len(commands_table))


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
        if self.object is not None:
            with session() as s:
                self.object.connected = False
                self.object.connection = None
                s.add(self.object)

    @property
    def object(self):
        if self.object_id is not None:
            return Character.get(self.object_id)

    @object.setter
    def object(self, character):
        if character is None:
            self.object_id = None
            return
        self.logger.info('Authenticated as %s.', character.name)
        self.object_id = character.id
        character.connection = self
        character.connected = True

    def notify(self, string):
        """Send a string of text to this connection."""
        self.sendLine(string.encode())

    def lineReceived(self, line):
        """A line was received."""
        line = line.decode(encoding, 'replace')
        with session() as s:
            if self.username is None:
                self.username = line.lower()
                if line == config.new_character_command:
                    msg = 'Enter a name for your new character:'
                else:
                    msg = 'Password:'
                return self.notify(msg)
            elif self.object is None:
                if self.username == config.new_character_command:
                    if Character.query(
                        func.lower(Character.name) == line
                    ).count():
                        return self.notify(
                            'That character name is taken. Please choose '
                            'another.'
                        )
                    elif not line:
                        self.notify(
                            'Character names cannot be blank. Goodbye.'
                        )
                        return self.transport.loseConnection()
                    else:
                        c = Character(name=line.title())
                        s.add(c)
                        s.commit()
                        self.object = c
                        self.notify(
                            f'Your new password is {c.randomise_password()}.'
                        )
                else:
                    c = Character.query(
                        func.lower(Character.name) == self.username
                    ).first()
                    if c is None or not c.check_password(line):
                        self.notify('Incorrect password.')
                        self.username = None
                        return self.notify('Username:')
                    else:
                        self.object = c
                # All checks should have been performed now. Let's tell the
                # user where they are.
                return self.object.show_location()
            if not line:
                return  # Just a blank line.
            if line[0] in config.command_substitutions:
                line = config.command_substitutions[line[0]] + line[1:]
            both = line.split(' ', 1)
            if len(both) == 1:
                both.append('')
            command, rest = both
            if command in commands_table and commands_table[
                command
            ].allowed(self.object):
                try:
                    return commands_table[command].run(self.object, rest)
                except Exception as e:
                    return self.object.notify(
                        'Something went wrong with your command.'
                    )
            direction = self.object.location.match_direction(line)
            if direction is None:
                return self.notify("I don't understand that.")
            commands_table['go'].run(self.object, direction.name)


class Factory(ServerFactory):
    """Store all connections."""

    connections = []
    shutdown_task = None

    def buildProtocol(self, addr):
        p = Protocol()
        p.factory = self
        logger.info('Incoming connection from %s:%d.', addr.host, addr.port)
        return p

    def broadcast(self, message):
        """Show a message to all connections."""
        for con in self.connections:
            con.notify(message)


factory = Factory()
