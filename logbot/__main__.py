from logbot.common import create_cfg_dirs, run_thread, register_listener
from logbot import log, httpd, bot, search, __version__

from pytz import timezone, UnknownTimeZoneError

from getpass import getuser, getpass

from os.path import exists, expanduser, join
import ConfigParser

class LogbotConfig(object):

    def __init__(self):
        self.default_options = {
            'logbot': {
                'user': None,
                'passwd': None,
                'host': 'localhost',
                'port': '5222',
                'tls': 'True',
                'timezone': None,
                'rooms': ''
                },
            'httpd': {
                'listen_address': '0.0.0.0',
                'listen_port': '5000'
            },
        }
        self.opts = {}
        self.opts.update(self.default_options['logbot'])
        self.opts.update(self.default_options['httpd'])

        self.config = ConfigParser.SafeConfigParser(self.opts, allow_no_value=True)

        sys_cfg = '/etc/logbot.ini'
        usr_cfg = join(expanduser('~/.logbot'), 'config')
        if exists(sys_cfg) or exists(usr_cfg):
            self.config.read([sys_cfg, usr_cfg])

    def get(self, section, item):
        try:
            return self.config.get(section, item)
        except ConfigParser.NoSectionError as e:
            if item in self.default_options[section]:
                return self.default_options[section][item]
            else:
                return None

    def getboolean(self, section, item):
        try:
            return self.config.getboolean(section, item)
        except ConfigParser.NoSectionError as e:
            if item in self.default_options[section]:
                if self.default_options[section][item] in ['True', 'true', 1, 0, 'T', 't']:
                    return True
                else:
                    return False
            else:
                raise Exception

    def items(self, section):
        return self.config.items(section)


def main(argv=None):
    import sys
    from argparse import ArgumentParser

    argv = argv or sys.argv

    config = LogbotConfig()

    parser = ArgumentParser(description='Jabber Log Bot')
    parser.add_argument('--user', help='jabber user', default=config.get('logbot', 'user'))
    parser.add_argument('--passwd', help='jabber password', default=config.get('logbot', 'passwd'))
    parser.add_argument('--host', help='jabber host', default=config.get('logbot', 'host'))
    parser.add_argument('--port', help='jabber port', default=config.get('logbot', 'port'), type=int)
    parser.add_argument('--no-tls', help='do not use tls', dest='use_tls',
                        action='store_false', default=config.getboolean('logbot', 'tls'))
    parser.add_argument('--version', action='version',
                        version='logbot {}'.format(__version__))
    parser.add_argument('--timezone', help='time zone', default=config.get('logbot', 'timezone'))
    parser.add_argument('rooms', help='rooms to log', nargs='+',
                        metavar='room')

    argv.extend(config.get('logbot', 'rooms').split())
    args = parser.parse_args(argv[1:].append(config.get('logbot', 'rooms')))

    if args.timezone:
        try:
            tz = timezone(args.timezone)
        except UnknownTimeZoneError:
            raise SystemExit(
                'error: unknown timezone - {}'.format(args.timezone))
    else:
        tz = None

    create_cfg_dirs(args.rooms)

    user = args.user or getuser()
    passwd = args.passwd or getpass()

    register_listener(log.log)
    register_listener(search.index)

    run_thread(httpd.run, [config.items('httpd')])

    bot.run(
        args.host,
        args.port,
        user,
        passwd,
        args.rooms,
        args.use_tls,
        tz=tz,
    )


if __name__ == '__main__':
    main()
