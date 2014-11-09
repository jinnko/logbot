from .common import publish, Message

from sleekxmpp import ClientXMPP

from datetime import datetime
from signal import signal, SIGINT

import logging
logging.basicConfig(level=logging.DEBUG)

def muc_event(room, name):
    return 'muc::{}::got_{}'.format(room, name)


def xmpp_user(msg):
    return msg.get('mucnick') or msg['from'].resource


class LogBot(ClientXMPP):
    def __init__(self, jid, password, rooms, nick, tz=None):
        logging.debug('Initializing LogBot')
        logging.debug(' - jid: %s' % jid)
        logging.debug(' - nick: %s' % nick)
        logging.debug(' - rooms: %s' % rooms)
        logging.debug(' - tz: %s' % tz)

        super(LogBot, self).__init__(jid, password)
        logging.debug('Initialized')
        self.rooms = rooms
        self.nick = nick
        self.tz = tz

        self.register_handlers(rooms)

    def register_handlers(self, rooms):
        logging.debug('Registering handlers')
        self.add_event_handler("session_start", self.session_start)
        self.add_event_handler("groupchat_message", self.publish)
        logging.debug('Registered handlers')

    def join_room(self, room):
        self.plugin['xep_0045'].joinMUC(room, self.nick, wait=True)
        for name, action in [('online', 'entered'), ('offline', 'left')]:
            logging.debug('Joining room %s, %s' % (room, name))
            event = muc_event(room, name)
            self.add_event_handler(event, self.muc_handler(room, action))
            logging.debug('Joined room')

    def muc_handler(self, room, action):
        logging.debug('much_handler: %s, %s, %s' % (evt, room, action))
        return lambda evt: self.on_status(evt, room, action)

    def session_start(self, event):
        logging.debug('Starting session')
        self.register_plugin('xep_0045')
        logging.debug('Sending presence')
        self.send_presence()
        logging.debug('Getting roster')
        self.get_roster()

        for room in self.rooms:
            self.join_room(room)

    def on_status(self, event, room, action):
        logging.debug('Received status message: %s %s %s' % (event, room, action))
        msg = {
            'from': event['from'],
            'body': '{} the room'.format(action),
        }
        self.publish(msg)

    def publish(self, xmpp_msg):
        logging.debug('Publish message: %s' % (xmpp_msg))
        msg = Message(
            user=xmpp_user(xmpp_msg),
            content=xmpp_msg['body'],
            time=datetime.now(tz=self.tz),
            room=xmpp_msg['from'].node,
        )
        publish(msg)


def run(host, port, user, passwd, rooms, use_tls=True, nick='logbot', tz=None):
    xmpp = LogBot(user, passwd, rooms, nick, tz)

    signal(SIGINT, lambda signum, frame: xmpp.disconnect())

    xmpp.connect((host, port), use_tls=use_tls)
    xmpp.process(block=True)
