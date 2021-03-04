import socket
import logging
from echo_server.solution.config import HOST, PORT

logging.basicConfig(format="%(asctime)s.%(msecs)03d\t%(message)s", datefmt="%H:%M:%S", level=logging.INFO)
logger = logging.getLogger("tcpserver")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    logger.info("Server is running")
    s.listen(1)
    logger.info("Server is listening")
    conn, addr = s.accept()
    with conn:
        logger.info(f"Connected by {addr[0]}:{addr[1]}")
        while data := conn.recv(1024):
            conn.send(data)
