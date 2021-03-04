import socket
from echo_server.solution.config import HOST, PORT, ENCODING, logger


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    logger.info(f"Connection to the server is established: '{HOST}:{PORT}'")
    while True:
        msg = input(f"{HOST}:{PORT}> ")
        print()
        if msg == "":
            continue

        s.sendall(msg.encode(ENCODING))
        logger.info(f"Sent data: -> {msg}")

        try:
            data = s.recv(1024).decode(ENCODING)
            logger.info(f"Received data: <- '{data}'")
        except ConnectionAbortedError:
            logger.info("Server broke the connection")
            break

        print(data)
