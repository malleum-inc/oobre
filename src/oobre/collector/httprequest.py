from twisted.web.resource import Resource
from twisted.web.server import Site
from urllib import unquote_plus
import sqlite3

from oobre.conntrack import get_connection


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, OOBRE Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


class CollectorProtocol(Resource):
    isLeaf = True

    def __init__(self, collector):
        Resource.__init__(self)
        self._collector = collector

    def render(self, request):
        self._collector.dataReceived(request.channel._connection,
                                    unquote_plus(request.uri.lstrip('/')))
        request.setHeader('Server', 'Apache/2.4.7 (Windows)')
        return '<html><body><h1>It works!</h1></body></html>'


class CollectorProtocolFactory(Site):

    def __init__(self, collector_class, name=None):
        Site.__init__(self, CollectorProtocol(collector_class(name)))

    def buildProtocol(self, addr):
        proto = Site.buildProtocol(self, addr)
        proto._connection = get_connection(addr)
        return proto
