import socket
from echo_server.solution.config import HOST, PORT

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen(1)
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr[0]}:{addr[1]}")
        while data := conn.recv(1024):
            conn.send(data)
