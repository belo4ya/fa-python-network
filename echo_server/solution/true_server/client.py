import socket

from package import Package

HOST, PORT = "localhost", 9999


def client(ip, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("localhost", 8910))
        sock.connect((ip, port))
        sock.sendall(message)
        response = Package.from_bytes(sock.recv(4096))
        print("Received: {}".format(response))


data = Package(headers={"encoding": "utf-8",
                        "username": "admin",
                        },
               cookies={"auth": 123,
                        "session-token": "be429bde-f173-485f-974d-3e0788a8450c"},
               content="Hello, world!")
client(HOST, PORT, data.to_bytes())
