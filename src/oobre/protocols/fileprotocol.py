from twisted.internet import protocol

__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, OOBRE Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


class FileProtocol(protocol.Protocol):

    def connectionMade(self):
        self.transport.write(file(self.file, 'rb').read())
        self.transport.loseConnection()

    def setFile(self, file_):
        self.file = file_


class FileProtocolFactory(protocol.Factory):

    def __init__(self, file_):
        self.file = file_

    def buildProtocol(self, addr):
        proto = FileProtocol()
        proto.setFile(self.file)
        return proto