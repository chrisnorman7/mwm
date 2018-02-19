"""Main entry point."""

import logging
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from twisted.internet import reactor
import config
from util import server_version

parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

parser.add_argument(
    '-c', '--config-file', default='game.yaml',
    help='The configuration file to use'
)

parser.add_argument(
    '-l', '--log-level', default='INFO',
    help='The default logging level'
)


def main(args):
    try:
        logging.basicConfig(level=args.log_level)
    except ValueError as e:
        print('Unable to initialise logging: %s' % e)
        raise SystemExit
    logging.info('Starting the server...')
    logging.info('Version: %s.', server_version())
    config.config = config.Config.load(args.config_file)
    from db import load_db, dump_db
    load_db()
    from networking import factory
    listener = reactor.listenTCP(
        config.config.port, factory, interface=config.config.interface
    )
    logging.info('Listening on %s:%d.', listener.interface, listener.port)
    from log_handler import LogHandler
    logging.getLogger().addHandler(LogHandler())
    reactor.run()
    logging.info('Server shutting down.')
    dump_db()
    config.config.dump(args.config_file)


if __name__ == '__main__':
    args = parser.parse_args()
    main(args)
