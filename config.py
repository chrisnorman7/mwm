"""Server configuration."""

import logging
import os
from attr import attrs, attrib, Factory, asdict
from yaml import load, dump

__all__ = ['Config']
logger = logging.getLogger(__name__)


@attrs
class Config:
    """Main server configuration."""

    port = attrib(default=Factory(lambda: 4000))
    interface = attrib(default=Factory(lambda: '0.0.0.0'))
    motd = attrib(default=Factory(lambda: 'Message of the day goes here'))
    db_file = attrib(default=Factory(lambda: 'world.yaml'))

    @classmethod
    def load(cls, filename):
        """Return a fully-loaded Config instance."""
        if os.path.isfile(filename):
            logger.info('Loading configuration from %s.', filename)
            with open(filename, 'r') as f:
                y = load(f)
                if not isinstance(y, dict):
                    logger.warning('Improperly formatted configuration file.')
                else:
                    return cls(**y)
        else:
            logger.info('Creating default configuration.')
        return cls()

    def dump(self, filename):
        """Dump configuration to disk."""
        logger.info('Dumping configuration to %s.', filename)
        d = asdict(self)
        with open(filename, 'w') as f:
            dump(d, f)
