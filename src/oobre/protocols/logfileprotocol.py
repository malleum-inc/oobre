from fcntl import flock
import logging
from twisted.internet import protocol
from twisted.python import log
from twisted.python.logfile import DailyLogFile

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, OOBRE Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


class LogFileProtocol(protocol.Protocol):

    def connectionMade(self):
        peer = self.transport.getPeer()
        print 'Got %s connection from %s:%s' % (peer.type, peer.host, peer.port)

    def dataReceived(self, data):
        self.logger.debug(repr(data))

    def setFile(self, file_):
        self.logger = logging.Logger('oobre')
        handler = logging.FileHandler(file_)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.DEBUG)


class LogFileProtocolFactory(protocol.Factory):

    def __init__(self, file_):
        self.file = file_

    def buildProtocol(self, addr, ):
        proto = LogFileProtocol()
        proto.setFile(self.file)
        return proto
