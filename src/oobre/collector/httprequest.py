from twisted.web.resource import Resource
from twisted.web.server import Site
from urllib import unquote_plus

from oobre.collector import Collector


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

    def __init__(self, collector_class):
        Resource.__init__(self)
        self.collector = collector_class()

    def render_DO(self, request):
        self.collector.dataReceived(unquote_plus(request.uri.lstrip('/')))
        request.setHeader('Server', 'Apache/2.4.7 (Windows)')
        return '<html><body><h1>It works!</h1></body></html>'

    def __getattr__(self, item):
        if item.startswith('render_'):
            return self.render_DO


class CollectorProtocolFactory(Site):

    def __init__(self, collector_class):
        Site.__init__(self, CollectorProtocol(collector_class))
