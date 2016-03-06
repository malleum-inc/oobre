from twisted.internet import protocol, utils, reactor
from twisted.python import failure
from cStringIO import StringIO

from re import compile

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, OOBRE Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


class ProcessProtocol(protocol.Protocol):

    split_s = compile(r'\s+')

    def setProcess(self, process):
        self.args = self.split_s.split(process)
        self.process = self.args.pop(0)

    def connectionMade(self):
        output = utils.getProcessOutput(self.process, self.args)
        output.addCallbacks(self.writeResponse, self.noResponse)

    def writeResponse(self, resp):
        self.transport.write(resp)
        self.transport.loseConnection()

    def noResponse(self, err):
        self.transport.loseConnection()


class ProcessProtocolFactory(protocol.Factory):

    protocol = ProcessProtocol

    def __init__(self, process):
        self.process = process

    def buildProtocol(self, addr):
        protocol = ProcessProtocol()
        protocol.setProcess(self.process)
        return protocol