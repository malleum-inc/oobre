# Installation

```console
easy_install twisted
pushd deps/pynetfilter_conntrack
python setup.py install
popd
python setup.py install
```

# Running OOBRE

```console
cd server
./start.sh
```

# Stopping OOBRE

```console
cd server
./stop.sh
```

# Configuring Rules

Rules must contain the following elements:

* Critera (optional): this specifies what OOBRE should look for when determining what action to take on a given port.
  Criteria directives include: `dport`, `sport`, `dst`, `src`, `hello`, and `knock`.

* Actions: this tells OOBRE how to handle an inbound connection for a given criteria. Valid actions include: `forward`,
  `factory`, `exec` (TODO).

The `dport`, `sport`, `dst`, and `src` criteria directives refer to the destination port, source port, destination IP
address, and source IP address, respectively. The `knock` and `hello` directives can be used to implement a port
knocking sequence (implemented as a sequence of bytes received prior to original protocol data reception), or a client
banner (i.e. `GET / HTTP/1.1`) that OOBRE should expect prior to routing a connection, respectively. A connection can
specify both a `hello` and `knock` directive at the same time. `hello` and `knock` are both matched using the regular
expression `re.match()` function.

The `forward` action instructs OOBRE to forward the connection to a destination IP and port using a specific protocol.
The format for `forward` directives is:

`forward=<tcp|udp>:<dst_ip>:<dst_port>`

Currently only `tcp` is supported but plans to implement `udp` are ongoing.

The `factory` action instructs OOBRE to use an instance of a twisted python TCP protocol factory to handle the inbound
connection. The absolute name of the factory class should be provided (i.e. `foo.mod.EchoFactory`). Make sure that the
python module sits in a directory that's in your Python sys.path. The format for `factory` directives is:

`factory=<some.mod.MyProtoFactory>`

With OOBRE you don't have to dedicate a port to a certain service. It is fully capable of multiplexing protocols
provided these protocols expect their clients to send the first set of bytes to the server. The way OOBRE determines
which action to take is based on the `hello` criteria. For example, the default rule-set in `server/oobre.rules` multiplexes SSH and
HTTP over port 80 (note: older version of SSH clients do not send the first few bytes to the server so this may not
work).

Another thing to note with the rule-sets in `server/oobre.rules` is that the SSH server expects the client to send `howdy` before
initiating the conversation with the backend SSH server. This can be achieved with the `knock` python script (which
gets installed on your machine), like so:

```console
$ knock howdy ssh root@mybox -p 80
```

Since there is only one protocol being handled after the knock sequence, the `hello` criteria directive is redundant.
However, if we required our clients to knock prior to giving them access to the web server then the `hello` directive
for both servers would be necessary.

Finally, if you are going to run OOBRE on your servers and decide you need to kill it temporarily, PLEASE MAKE SURE
YOU USE SIGNAL 15 AND NOT 9. Otherwise, YOU WILL NOT BE ABLE TO CONNECT to the server. OOBRE uses iptables to be able
to "listen" on all ports using a simple port redirect hack. If you shutdown OOBRE uncleanly, this iptable hack will
render your machine inaccessible and you will either need physical access to the machine or ask for KVM support.
