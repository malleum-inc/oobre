from twisted.internet import protocol

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, OOBRE Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


class LogProtocol(protocol.Protocol):

    def connectionMade(self):
        peer = self.transport.getPeer()
        print 'Got %s connection from %s:%s' % (peer.type, peer.host, peer.port)


class LogProtocolFactory(protocol.Factory):

    protocol = LogProtocol
