import socket
import time

from package import Package

HOST, PORT = "localhost", 9999


def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        print(f"Message: {message}")
        sock.bind(("localhost", 8910))
        sock.connect((ip, port))
        sock.sendall(message)
        response = Package.from_bytes(sock.recv(4096))
        print(f"Received: {response}")

        response.content = "Now, I authorized! How are you?"
        client(ip, port, response.to_bytes())
        time.sleep(1)


data = Package(headers={
    "encoding": "utf-8",
    "username": "admin",
    "password": "admin"
}, content="Hello, world!")
client(HOST, PORT, data.to_bytes())
