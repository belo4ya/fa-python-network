import socket
from echo_server.solution.config import HOST, PORT, ENCODING, logger


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    logger.info(f"Server is running: {PORT}:{HOST}")
    s.listen(1)
    logger.info("Server is listening")
    try:
        while True:
            conn, addr = s.accept()
            with conn:
                logger.info(f"Connected by <<{addr[0]}:{addr[1]}>>")
                while True:

                    try:
                        data = conn.recv(1024).decode(ENCODING)
                    except ConnectionResetError:
                        logger.info(f"Client has terminated the connection\n" +
                                    "=" * 50 + "\n")
                        break

                    if not data:
                        break

                    if data.lower() == "shutdown":
                        raise KeyboardInterrupt

                    logger.info(f"Received data: <- '{data}'")
                    conn.send(data.encode(ENCODING))
                    logger.info(f"Sent data: -> '{data}'")
    except KeyboardInterrupt:
        logger.info("Server is turned off")
