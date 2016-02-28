from twisted.internet import protocol

from oobre.conntrack import get_connection
from oobre.ruleengine import parse_rules, get_protocol


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, OOBRE Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'


class Router(protocol.Factory):
    def __init__(self, rule_file):
        parse_rules(rule_file)

    def buildProtocol(self, address):
        c = get_connection(address)
        proto = get_protocol(c)
        if not proto:
            print '*** Got unknown %s connection from %s on port %s. ***' % (address.type.upper(), address.host, c.dport)
        return proto