import socket
from echo_server.solution.config import HOST, PORT, ENCODING


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        s.sendall(input(f"{HOST}:{PORT}> ").encode(ENCODING))
        data = s.recv(1024)
        print(data.decode(ENCODING))
