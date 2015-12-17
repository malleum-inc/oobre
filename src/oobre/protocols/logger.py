from twisted.internet import protocol

__author__ = 'root'


class LogProtocol(protocol.Protocol):

    def connectionMade(self):
        peer = self.transport.getPeer()
        print 'Got %s connection from %s:%s' % (peer.type, peer.host, peer.port)


class LogProtocolFactory(protocol.Factory):

    protocol = LogProtocol
