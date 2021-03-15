import selectors
import socket
import time
import logging
from echo_server.solution.config import HOST, PORT

logging.basicConfig(filename="log.txt",
                    format="%(asctime)s.%(msecs)03d\t%(message)s",
                    datefmt="%H:%M:%S",
                    level=logging.INFO)


class SimpleChat:

    def __init__(self, host, port):
        self.main_socket = socket.socket()
        self.main_socket.bind((host, port))
        self.main_socket.listen(10)
        self.main_socket.setblocking(False)

        self.selector = selectors.DefaultSelector()
        self.selector.register(fileobj=self.main_socket, events=selectors.EVENT_READ, data=self.on_accept)

        self.peers = {}
        self.logger = logging.getLogger("")

    def on_accept(self, sock, mask):
        conn, addr = self.main_socket.accept()
        logger.info(f'accepted connection from {addr}')
        conn.setblocking(False)

        self.peers[addr] = conn
        self.selector.register(fileobj=conn, events=selectors.EVENT_READ, data=self.on_read)

    def on_close(self, conn):
        addr = conn.getpeername()
        conn = self.peers[addr]
        logger.info(f'closing connection to {addr}')
        self.peers.pop(addr)
        self.selector.unregister(conn)
        conn.close()

    def on_read(self, conn, mask):
        try:
            data = conn.recv(1024)
            if data:
                peername = conn.getpeername()
                logger.info(f'got data from {peername}')
                for peer in self.peers.values():
                    if peer != conn:
                        peer.send(data)
            else:
                self.on_close(conn)
        except ConnectionResetError:
            self.on_close(conn)

    def run_forever(self):
        last_report_time = time.time()
        logger.info('starting')

        while True:
            events = self.selector.select(timeout=0.05)

            for key, mask in events:
                handler = key.data
                handler(key.fileobj, mask)

            current_time = time.time()
            if current_time - last_report_time > 5:
                logger.info(f'Num active peers = {len(self.peers)}')
                last_report_time = current_time


if __name__ == '__main__':
    server = SimpleChat(host=HOST, port=PORT)
    server.run_forever()
