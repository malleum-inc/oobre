from collections import namedtuple
import re

__author__ = 'root'


__all__ = [
    'get_connection'
]


conntrack_m = re.compile('(?:([^=\s]+)=)?([^\s]+)')
fixline_r = re.compile('(src|dst|sport|dport)')


class Connection(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def read_conn_track():
    connections = []
    with file('/proc/net/ip_conntrack') as f:
        for l in f.readlines():
            l = fixline_r.sub('o\\1', l, 4)
            details = conntrack_m.findall(l)
            proto = details.pop(0)[1]
            conn = dict([(k, int(v) if 'port' in k else v) for k, v in details])
            del conn['']
            conn['protocol'] = proto
            connections.append(conn)
    return connections


def get_connection(address):
    for c in read_conn_track():
        if c['osrc'] == address.host and c['protocol'] == address.type.lower() and c['osport'] == address.port:
            return Connection(
                src=address.host,
                dst=c['odst'],
                protocol=address.type,
                sport=address.port,
                dport=c['odport'],
                hello='',
                address=address
            )