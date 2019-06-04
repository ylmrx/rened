import os
import socket
import select
import json
import click
import multiprocessing
import sys
import paramiko
import logging
import colorlog

try:
    import SocketServer
except ImportError:
    import socketserver as SocketServer

class ForwardServer(SocketServer.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True

class Handler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            chan = self.ssh_transport.open_channel(
                "direct-tcpip",
                (self.chain_host, self.chain_port),
                self.request.getpeername(),
            )
        except Exception as e:
            self.log.debug("Incoming request to %s:%d failed: %s"
                % (self.chain_host, self.chain_port, repr(e)))
            return
        if chan is None:
            self.logger.debug("Incoming request to %s:%d was rejected by the SSH server."
                % (self.chain_host, self.chain_port))
            return

        self.log.debug("Connected!  Tunnel open %r -> %r -> %r"
            % (self.request.getpeername(),
                chan.getpeername(),
                (self.chain_host, self.chain_port)))
        while True:
            r, w, x = select.select([self.request, chan], [], [])
            if self.request in r:
                data = self.request.recv(1024)
                if len(data) == 0:
                    break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0:
                    break
                self.request.send(data)

        peername = self.request.getpeername()
        chan.close()
        self.request.close()
        self.log.debug("Tunnel closed from %r" % (peername,))

def forward_tunnel(local_port, remote_host, remote_port, transport, logger):
    # this is a little convoluted, but lets me configure things for the Handler
    # object.  (SocketServer doesn't give Handlers any way to access the outer
    # server normally.)
    class SubHandler(Handler):
        chain_host = remote_host
        chain_port = remote_port
        ssh_transport = transport
        log = logger

    ForwardServer(("", local_port), SubHandler).serve_forever()

def ssh_tunnel(c, logger):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    logger.info("Connecting to ssh host %s:%d ..." % (c['rhost'], int(c['rport'])))

    try:
        client.connect(
            c['rhost'],
            c['rport'],
            username=c['user'],
            compress=c['compression']
        )
    except Exception as e:
        logger.error("*** Failed to connect to %s:%d: %r" % (c['rhost'], c['rport'], e))
        sys.exit(1)

    logger.info("Now forwarding port %d to %s:%d ..."
        % (c['localport'], c['fhost'], c['fport']))
    forward_tunnel(c['localport'], c['fhost'], c['fport'], client.get_transport(), logger)
    
@click.command()
@click.argument('config', type=click.File('rb'),
                default=os.path.join(os.getenv('HOME'), '.rened.json'))
@click.option('--verbose', '-v',
              help="more infos on stdout", 
              is_flag=True)

def main(config, verbose):
    processlist = []
    logger = logging.getLogger()

    handler = logging.StreamHandler()
    handler.setFormatter(colorlog.ColoredFormatter( \
                    ' %(log_color)s%(name)s/%(levelname)-8s%(reset)s |'
                    ' %(log_color)s%(message)s%(reset)s'))

    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if verbose else logging.ERROR)

    conf = json.load(config)

    for t in conf['tunnels']:
        tun = conf['tunnels'].get(t)
        for k in [
                    'user', 
                    'fhost',
                    'compression',
                    'rport'
                ]:
            if k not in tun.keys():
                conf['tunnels'][t][k] = conf['settings']['default_' + k]
        p = multiprocessing.Process(target=ssh_tunnel, 
                                    args=(tun, logger))

        p.start()
        processlist.append(p)
    
    try:
        for p in processlist:
            p.join()
    except KeyboardInterrupt:
        for p in processlist:
            p.terminate()
        logger.info("C-c: Port forwarding stopped.")
        sys.exit(0)

if __name__ == "__main__":
    main()