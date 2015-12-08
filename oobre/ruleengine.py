import importlib
import shlex
from collections import defaultdict, namedtuple
import re

from twisted.protocols.portforward import ProxyFactory as KnockingProxyFactory
from oobre.protocols.portforwarder import ProxyFactory
from oobre.protocols.routingprotocol import RoutingProtocolFactory


__author__ = 'root'


routing_rules = defaultdict(list)

RoutingCriteria = namedtuple('RoutingCriteria', ['protocol', 'src', 'dst', 'sport', 'dport', 'hello'])


class RouteMatcher(object):

    def __init__(self, criteria):
        self._criteria = criteria
        self._matcher = re.compile(self._criteria.hello or '.')

    def is_match(self, connection, match_hello=True):
        if self._criteria.protocol and self._criteria.protocol.lower() != connection.protocol.lower():
            return False
        # TODO: for dst and src we should support ranges of IPs and subnets
        if self._criteria.src and self._criteria.src != connection.src:
            return False
        if self._criteria.dst and self._criteria.dst != connection.dst:
            return False
        if self._criteria.sport and connection.sport not in self._criteria.sport:
            return False
        if self._criteria.dport and connection.dport not in self._criteria.dport:
            return False
        if match_hello and self._criteria.hello and (not connection.hello or not self._matcher.match(connection.hello)):
            return False
        return True


class RoutingRule(object):
    # TODO: support generic 'knock' and 'hello' criteria for port knocking plus protocol multiplexing

    criteria_options = [
        'protocol',
        'src',
        'dst',
        'dport',
        'sport',
        'hello'
    ]

    actions = {
        'forward',
        'exec',
        'file',
        'factory',
        'knock_forward'
    }

    def __init__(self, rule):
        self._factory = None

        options = dict([o.split('=', 1) for o in shlex.split(rule)])
        options = {k: self._parse_port(v) if 'port' in k else v for k, v in options.iteritems()}

        if not self.actions.intersection(options):
            raise RuntimeError('You must specify one of the following options: protocol, forward, exec, or file')
        elif options.get('factory'):
            self._factory = self._import_class(options['factory'])()
        elif options.get('forward'):
            protocol, host, port = options['forward'].lower().split(':', 2)
            if protocol == 'tcp':
                self._factory = ProxyFactory(host, int(port))
            elif protocol == 'udp':
                raise NotImplementedError('The UDP protocol forwarder has not been implemented yet.')
            else:
                raise ValueError('Invalid protocol forwarding option (%r). Must be either tcp or udp' % protocol)
        elif options.get('knock_forward'):
            protocol, host, port = options['knock_forward'].lower().split(':', 2)
            if protocol == 'tcp':
                self._factory = KnockingProxyFactory(host, int(port))
            elif protocol == 'udp':
                raise NotImplementedError('The UDP protocol forwarder has not been implemented yet.')
            else:
                raise ValueError('Invalid protocol forwarding option (%r). Must be either tcp or udp' % protocol)
        elif options.get('exec'):
            raise NotImplementedError('The exec option has not been implemented yet.')
        elif options.get('file'):
            raise NotImplementedError('The file option has not been implemented yet.')

        self._criteria = RoutingCriteria(**{k: options.get(k) for k in self.criteria_options})

        self._matcher = RouteMatcher(self._criteria)

        self._needs_data = bool(options.get('hello') or isinstance(self._factory, KnockingProxyFactory))

    @staticmethod
    def _import_class(name):
        module_name, class_name = name.rsplit('.', 1)
        return getattr(importlib.import_module(module_name), class_name)

    @property
    def factory(self):
        return self._factory

    @property
    def criteria(self):
        return self._criteria

    @property
    def matcher(self):
        return self._matcher

    def matches(self, connection, match_hello=True):
        return self._matcher.is_match(connection, match_hello)

    @property
    def needs_data(self):
        return self._needs_data

    def _parse_port(self, port):
        if port is None:
            return None
        if ',' in port:
            ports = []
            for p in port.split(','):
                ports.extend(self._parse_port(p))
            return set(ports)
        elif '-' in port:
            port_range = [int(i) for i in port.split('-', 1)]
            port_range.sort()
            port_range[1] += 1
            return xrange(*port_range)
        port = int(port)
        return [port]


def get_rule_key(port, protocol):
    return '%s/%s' % (port, (protocol or 'tcp').lower()) if port or protocol else None


def parse_rules(rule_file):
    with file(rule_file) as f:
        for l in f.readlines():
            if l.strip().startswith('#'):
                continue
            rr = RoutingRule(l)
            print rr.criteria
            if rr.criteria.dport:
                for dport in rr.criteria.dport:
                    routing_rules[get_rule_key(dport, rr.criteria.protocol)].append(rr)
            else:
                routing_rules[None].append(rr)


def get_protocol(connection):
    rrs = list(routing_rules.get(get_rule_key(connection.dport, connection.protocol), []))
    default_rrs = routing_rules.get(None, [])
    num_rr = len(rrs)

    # Check for strict matching routing rules
    if num_rr == 1:
        if rrs[0].matches(connection, False):
            if rrs[0].needs_data:
                return RoutingProtocolFactory(rrs).buildProtocol(connection.address, connection)
            return rrs[0].factory.buildProtocol(connection.address)
    elif num_rr > 1:
        rrs.extend(default_rrs)
        return RoutingProtocolFactory(rrs).buildProtocol(connection.address, connection)

    # Check for any any routing rules
    if default_rrs:
        return RoutingProtocolFactory(default_rrs).buildProtocol(connection.address, connection)
    return None