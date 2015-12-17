from twisted.internet import protocol


class EchoProtocol(protocol.Protocol):

    def dataReceived(self, data):
        self.transport.write(data)
        self.transport.loseConnection()


class EchoFactory(protocol.Factory):
    protocol = EchoProtocol

