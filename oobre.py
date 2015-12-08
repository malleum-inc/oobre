from twisted.internet import reactor
from twisted.internet.endpoints import TCP4ServerEndpoint
import sys

from oobre.router import Router

LISTEN_PORT = 8080

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'usage: %s <rule_file>' % sys.argv[0]
        exit(-1)
    TCP4ServerEndpoint(reactor, LISTEN_PORT).listen(Router(sys.argv[1]))
    reactor.run()
