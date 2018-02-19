"""Provides the Protocol class for communicating with clients."""

import logging
import sys
from socket import gethostbyaddr, gaierror
from datetime import datetime
from inspect import isclass
from sqlalchemy import func
from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory
from twisted.protocols.basic import LineReceiver
import commands
from commands.base import Command
from db import Character, session, RoomCommand, Room, MatchError
from config import config
from programming import manage_environment

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
n = len(set(commands_table.values()))
if not n:
    logger.warning('No commands loaded. Run build-commands.py first.')
    raise SystemExit
else:
    logger.info('Commands loaded: %d.', n)


class Protocol(LineReceiver):

    @property
    def connected_time(self):
        return datetime.utcnow() - self.connected_at

    @property
    def idle_time(self):
        return datetime.utcnow() - self.idle_since

    def reset_logger(self):
        """Set the logger with an appropriate name."""
        self.logger = logging.getLogger('%s:%d' % (self.host, self.port))

    def resolve_host(self):
        """Try and get the proper hostname for this connection."""
        try:
            res = gethostbyaddr(self.host)
        except gaierror:
            return  # Do nothing.
        self.host = res[0]
        self.reset_logger()

    def connectionMade(self):
        now = datetime.utcnow()
        self.connected_at = now
        self.idle_since = now
        self.object_id = None
        self.intercept = None
        peer = self.transport.getPeer()
        self.host = peer.host
        self.port = peer.port
        reactor.callInThread(self.resolve_host)
        self.reset_logger()
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

    def set_intercept(self, i):
        """Intercept this connection with an instance of Intercept i."""
        self.intercept = i
        i.connection = self

    def lineReceived(self, line):
        """A line was received."""
        self.idle_since = datetime.utcnow()
        line = line.decode(encoding, 'replace')
        with session() as s:
            if self.intercept is not None:
                return self.intercept.feed(line)
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
                        c.location = Room.first()
                        s.commit()
                        self.object = c
                        self.logger.info('Created character %s.', c)
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
            if self.object is not None and self.object.log_commands:
                self.object.log_command(line)
            command, rest = both
            if command in commands_table and commands_table[
                command
            ].allowed(self.object):
                try:
                    return commands_table[command].run(self.object, rest)
                except MatchError as e:
                    self.object.notify(str(e))
                except Exception as e:
                    return self.object.notify(
                        'Something went wrong with your command.'
                    )
            cmd = RoomCommand.query(
                name=command, location_id=self.object.location_id
            ).first()
            if cmd is not None:
                try:
                    with manage_environment(
                        character=self.object, here=self.object.location,
                        text=rest
                    ) as lua:
                        lua.execute(cmd.code)
                except MatchError as e:
                    self.object.notify(str(e))
                except Exception as e:
                    self.notify('There was a problem with your command.')
                    logger.warning('Room command %s caused an error:', cmd)
                    logger.exception(e)
                return
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
started = datetime.utcnow()


def uptime():
    """Returns how long the server has been running."""
    return datetime.utcnow() - started
