from twisted.internet import protocol
import re

from pymemcache.client.base import Client
from src.oobre.conntrack import get_connection


__author__ = 'root'


class EchoProtocol(protocol.Protocol):

    def __init__(self, *args, **kwargs):
        self._memcache = Client(('localhost', 11211))

    def dataReceived(self, data):
        c = get_connection(self.transport.getPeer())
        knocks = self._memcache.get(c.src)

        knock = 'port=%s;hello=%s' % (c.dport, data.strip())
        print repr(knock)

        if not knocks or ',' in knock or not knocks.startswith(knock):
            self.transport.write('ECHO ECho Echo echo: %s\nPerhaps another port?\n' % data.strip())
            self.transport.loseConnection()
        else:
            knocks = re.sub('^%s,?' % knock, '', knocks, 1)
            self._memcache.set(c.src, knocks, 30)
            if knocks:
                self.transport.write('Good! Now onto the next one! 30 seconds left! Tick tock!')
            else:
                self.transport.write('You got it! flag{p0rt_kn0ck1ng_1s_fUn_&_31337}\n')
            self.transport.loseConnection()



class EchoFactory(protocol.Factory):
    protocol = EchoProtocol

