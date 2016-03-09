import atexit
import subprocess
import signal
from twisted.application import internet, service
from twisted.internet import reactor

from oobre.config import config
from oobre.router import Router


__author__ = 'Nadeem Douba'
__copyright__ = 'Copyright 2012, OOBRE Project'
__credits__ = []

__license__ = 'GPL'
__version__ = '0.1'
__maintainer__ = 'Nadeem Douba'
__email__ = 'ndouba@gmail.com'
__status__ = 'Development'

RULE_FILE = 'oobre.rules'


def restore_ipt():
    if hasattr(restore_ipt, 'restored'):
        return
    restore_ipt.restored = True
    print 'Removing iptable rule from PREROUTING NAT table.'
    p = subprocess.Popen(['iptables', '-D', 'PREROUTING', '-t', 'nat', '-i', restore_ipt.interface, '-p',
                          'tcp', '-j', 'REDIRECT', '--to-port', str(restore_ipt.listen_port)])
    p.communicate()


def register_ipt(interface, listen_port):
    print 'Registering iptable rule in PREROUTING NAT table.'
    p = subprocess.Popen(['iptables', '-A', 'PREROUTING', '-t', 'nat', '-i', interface, '-p',
                          'tcp', '-j', 'REDIRECT', '--to-port', str(listen_port)])
    p.communicate()


def quit_handler(signum, frame):
    print 'Caught signal', signum
    restore_ipt()
    reactor.callFromThread(reactor.stop)


old_sigint = signal.signal(signal.SIGINT, quit_handler)
old_sigterm = signal.signal(signal.SIGTERM, quit_handler)
old_sighup = signal.signal(signal.SIGHUP, quit_handler)


def get_application():

    restore_ipt.listen_port = listen_port = config.get('oobre', 'listen_port')
    restore_ipt.interface = interface = config.get('oobre', 'interface')

    print 'Listening on port %s' % listen_port

    application = service.Application("OOBRE")
    routerService = internet.TCPServer(int(listen_port), Router(RULE_FILE))
    routerService.setServiceParent(application)

    atexit.register(restore_ipt)
    register_ipt(interface, listen_port)

    return application


application = get_application()