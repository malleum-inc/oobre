from collections import namedtuple
import re
import os
import subprocess

__author__ = 'root'


__all__ = [
    'get_connection'
]


conntrack_m = re.compile('(?:([^=\s]+)=)?([^\s]+)')
fixline_r = re.compile('(src|dst|sport|dport)')


def parse_event(l):
    l = fixline_r.sub('o\\1', l, 4)
    details = conntrack_m.findall(l)
    proto = details.pop(0)[1]
    c = dict([(k, int(v) if 'port' in k else v) for k, v in details])
    del c['']
    c['protocol'] = proto
    return c


class Connection(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def read_conn_track():
    connections = []
    
    if os.path.lexists('/proc/net/ip_conntrack'):
        with file('/proc/net/ip_conntrack') as f:
            for l in f.readlines():
                connections.append(parse_event(l))
    else:
        p = subprocess.Popen(['conntrack', '-L'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        for l in out.split('\n'):
            if 'ESTABLISHED' in l and 'dport' in l:
                connections.append(parse_event(l))
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
