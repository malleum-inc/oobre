from twisted.internet import protocol
from twisted.protocols.portforward import ProxyFactory as KnockingProxyFactory

from oobre.protocols.portforwarder import ProxyFactory


__author__ = 'root'


class RoutingProtocol(protocol.Protocol):

    def _swap_transport(self, client):
        client.makeConnection(self.transport)
        self.transport.protocol = client

    def dataReceived(self, data):
        client = None
        self._connection.hello = data
        for rr in self._rules:
            if rr.matches(self._connection):
                if isinstance(rr.factory, ProxyFactory):
                    client = rr.factory.buildProtocol(self._connection.address, data)
                    self._swap_transport(client)
                elif isinstance(rr.factory, KnockingProxyFactory):
                    client = rr.factory.buildProtocol(self._connection.address)
                    self._swap_transport(client)
                else:
                    client = rr.factory.buildProtocol(self._connection.address)
                    self._swap_transport(client)
                    client.dataReceived(data)
                break
        if not client:
            print '*** Got unknown %s connection from %s on port %s with hello=%r. ***' % (
                self._connection.protocol.upper(),
                self._connection.src,
                self._connection.dport,
                self._connection.hello[:10]
            )
            self.transport.loseConnection()

    def setConnection(self, connection):
        self._connection = connection

    def setRules(self, rules):
        self._rules = rules


class RoutingProtocolFactory(protocol.Factory):

    protocol = RoutingProtocol

    def __init__(self, rules):
        self.rules = rules

    def buildProtocol(self, addr, connection=None):
        protocol = RoutingProtocol()
        protocol.setConnection(connection)
        protocol.setRules(self.rules)
        return protocol