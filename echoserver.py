from twisted.internet import protocol

__author__ = 'root'


class EchoProtocol(protocol.Protocol):
    def dataReceived(self, data):
        self.transport.write(data)


class EchoFactory(protocol.Factory):
    protocol = EchoProtocol

