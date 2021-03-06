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

    def handle(self):
        request = self.get_request()

        try:
            response = self.authorization(request)
            if not response:
                response = self.handle_request(self.get_request())
        except BaseError as e:
            response = self.handle_error(e, 400)

        return self.do_response(response)

    def handle_request(self, request):
        return request.to_bytes()

    def handle_error(self, e, status=400):
        status = e.status or status
        return package.Package(status=status, content=e.message)

    def get_request(self):
        raw_request = self.rfile.read(1024)
        while True:
            data = self.rfile.read(1024)
            if not data:
                break

            raw_request += data

        print(raw_request)
        return package.Package.from_bytes(raw_request)

    def do_response(self, response: package.Package):
        return self.wfile.write(response.to_bytes())

    def authorization(self, request):
        try:
            not_authorized = not self.is_authorized(request.headers, request.cookies)
        except AuthorizationError as e:
            return self.handle_error(e)

        if not_authorized:
            try:
                self.do_log_in(request.headers, request.cookies)
            except AuthorizationError as e:
                return self.handle_error(e)

    def do_log_in(self, headers, cookies):
        username = headers.get("username")
        password = headers.get("password")

        if username is None or password is None:
            raise AuthorizationError

        current_user = db.DataBase.session.query(db.User).filter_by(username=username).one_or_none()
        if current_user is None:
            raise UserNotExistError

        if hashlib.md5(password.encode()).hexdigest() != current_user.password:
            raise PasswordError

        session_token = str(uuid.uuid4())
        current_user.session_token = session_token

        session_start = datetime.datetime.now()
        current_user.session_start = session_start

        db.DataBase.session.add(current_user)
        db.DataBase.session.commit()

        return package.Package(status=200,
                               content=f"Authorization is successful!\nWelcome, {username}",
                               cookies={
                                   **cookies,
                                   "session-token": session_token,
                                   "session-start": session_start.strftime("%H:%M:%S - %m.%d.%Y")
                               })

    def is_authorized(self, headers, cookies):
        session_timeout = 15 * 60

        username = headers.get("username")
        if username is None:
            raise UsernameIsNoneError

        current_user = db.DataBase.session.query(db.User).filter_by(username=username).one_or_none()
        if current_user is None:
            raise UserNotExistError(username=username)

        session_token = current_user.session_token
        if session_token is None:
            return False

        session_start = current_user.session_start
        if session_start is None:
            return False

        if datetime.datetime.now() - session_start > datetime.timedelta(seconds=session_timeout):
            return False

        if session_token != cookies.get("session-token"):
            return False

        return True


class BaseError(Exception):

    def __init__(self, message="", status=None):
        self.message = message
        self.status = status


class AuthorizationError(BaseError):

    def __init__(self, message="", username=None, password=None, status=400):
        super(AuthorizationError, self).__init__(message, status)
        self.username = username
        self.password = password


class UserNotExistError(AuthorizationError):
    message = ""

    def __init__(self, username):
        super(UserNotExistError, self).__init__(message=self.message, username=username)


class UsernameIsNoneError(AuthorizationError):
    message = ""

    def __init__(self):
        super(UsernameIsNoneError, self).__init__(message=self.message)


class PasswordError(AuthorizationError):
    message = ""

    def __init__(self):
        super(PasswordError, self).__init__(message=self.message)


if __name__ == '__main__':
    HOST, PORT = "localhost", 9999
    with Server((HOST, PORT), Handler) as server:
        server.serve_forever()
