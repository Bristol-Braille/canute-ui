#!/usr/bin/env python
import argparse
import select
import socket
import pickle
import logging

log = logging.getLogger(__name__)

UDP_IP = "127.0.0.1"
TIMEOUT = 0.5


class udp_send():
    """helper class for communications between emulated driver and GUI

    :param port: port to send to
    """
    def __init__(self, port=5000):
        self.port = port
        self.sock = socket.socket(socket.AF_INET,  # Internet
                                 socket.SOCK_DGRAM)  # UDP
        log.debug("will send to port %d" % self.port)

    def put(self, message):
        self.sock.sendto(pickle.dumps(message), (UDP_IP, self.port))


class udp_recv():

    """helper class for communications between emulated driver and GUI

    :param port: port to listen on to
    """
    def __init__(self, port=5000):
        self.port = port
        self.sock = socket.socket(socket.AF_INET,  # Internet
                             socket.SOCK_DGRAM)  # UDP
        self.sock.setblocking(0)
        self.sock.bind((UDP_IP, self.port))
        log.debug("binding to port %d" % self.port)

    def get(self):
        ready = select.select([self.sock], [], [], TIMEOUT)
        if ready[0]:
            data = pickle.loads(self.sock.recv(4096))
            return data
        return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="udp test")

    parser.add_argument('--send', action='store_const', dest='send', const=True, default=False, help="send")
    parser.add_argument('--recv', action='store_const', dest='recv', const=True, default=False, help="receive")
    parser.add_argument('--port', action='store', dest='port', default=5000, help="port")

    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    log = logging.getLogger(__name__)

    if args.send:
        u = udp_send(args.port)
        msg = {"matt": "cool"}
        u.put(msg)
        log.info("sending %s" % msg)
    elif args.recv:
        u = udp_recv(args.port)
        log.info("got: %s" % u.get())
