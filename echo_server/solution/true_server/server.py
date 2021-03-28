import datetime
import hashlib
import logging
import threading
import uuid

import base
import db
import package

logging.basicConfig(format="%(asctime)s.%(msecs)03d\t%(message)s", datefmt="%H:%M:%S",
                    level=logging.INFO, filename=None)


class Server(base.BaseTCPServer):
    allow_reuse_address = True

    def server_bind(self):
        self.socket.setblocking(False)
        super(Server, self).server_bind()

        host, port = self.server_address
        logging.info(f"Server was bound:\t{host}:{port}")

    def server_activate(self):
        super(Server, self).server_activate()
        logging.info("Server started listening")

    def serve_forever(self, poll_interval=0.5):
        try:
            super(Server, self).serve_forever(poll_interval)
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        threading.Thread(target=super(Server, self).shutdown).start()

    def get_request(self):
        request, client_address = super(Server, self).get_request()
        host, port = client_address
        logging.info(f"New connection from:\t{host}:{port}")
        return request, client_address

    def close_request(self, request):
        host, port = request.getpeername()
        logging.info(f"Close connection:\t{host}:{port}")
        super(Server, self).close_request(request)

    def server_close(self):
        super(Server, self).server_close()
        logging.info(f"Server is closed")


class Handler(base.BaseTCPRequestHandler):

    def get_request(self):
        self.raw_request = self.rfile.read(1024)
        while True:
            data = self.rfile.read(1024)
            if not data:
                break

            self.raw_request += data

        return package.Package.from_bytes(self.raw_request)

    def do_response(self):
        try:
            self.wfile.write(self.response.to_bytes())
        except AttributeError:
            self.wfile.write(package.Package(content="Hello, world!").to_bytes())

    def log_in(self):
        username = self.request.headers.get("username")
        password = self.request.headers.get("password")

        if username is None or password is None:
            raise AuthorizationError

        current_user = db.DataBase.session.query(db.User).filter_by(username=username).one_or_none()
        if current_user is None:
            raise UsernameError

        print(hashlib.md5("admin".encode()).hexdigest())
        if hashlib.md5(password.encode()).hexdigest() != current_user.password:
            raise PasswordError

        session_token = str(uuid.uuid4())
        current_user.session_token = session_token

        session_start = datetime.datetime.now()
        current_user.session_start = session_start

        db.DataBase.session.add(current_user)
        db.DataBase.session.commit()

        self.response = package.Package(status=200,
                                        headers={"session-token": session_token,
                                                 "session-start": session_start.strftime("%H:%M:%S - %m.%d.%Y")},
                                        content=f"Authorization is successful!\nWelcome, {username}")

    def is_authorized(self):
        session_time = 15 * 60

        username = self.request.headers.get("username")
        if username is None:
            raise UsernameError

        current_user = db.DataBase.session.query(db.User).filter_by(username=username).one_or_none()
        if current_user is None:
            raise UsernameError

        session_token = current_user.session_token
        if session_token is None:
            return False

        session_start = current_user.session_start
        if session_start is None:
            return False

        if datetime.datetime.now() - session_start > datetime.timedelta(seconds=session_time):
            return False

        if session_token != self.request.cookies.get("session-token"):
            return False

        return True

    def handle(self):
        self.request = self.get_request()

        try:
            if not self.is_authorized():
                self.log_in()
        except UsernameError:
            self.response = package.Package(status=400, content="Username Error")
            return self.do_response()
        except PasswordError:
            self.response = package.Package(status=400, content="Password Error")
            return self.do_response()
        except AuthorizationError:
            self.response = package.Package(status=400, content="Authorization Error")
            return self.do_response()

        return self.do_response()


class AuthorizationError(Exception):
    pass


class UsernameError(AuthorizationError):
    pass


class PasswordError(AuthorizationError):
    pass


if __name__ == '__main__':
    HOST, PORT = "localhost", 9999
    with Server((HOST, PORT), Handler) as server:
        server.serve_forever()
