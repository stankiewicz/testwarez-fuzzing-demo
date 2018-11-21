import socket
from kitty.targets.server import ServerTarget


class TcpTarget(ServerTarget):


    def __init__(self, name, host, port, timeout=None, logger=None):
        super(TcpTarget, self).__init__(name, logger,expect_response=True)
        self.host = host
        self.port = port
        if (host is None) or (port is None):
            raise ValueError('host and port may not be None')
        self.timeout = timeout
        self.socket = None

    def pre_test(self, test_num):
        super(TcpTarget, self).pre_test(test_num)
        if self.socket is None:
            sock = self._get_socket()
            if self.timeout is not None:
                sock.settimeout(self.timeout)
            sock.connect((self.host, self.port))
            self.socket = sock

    def _get_socket(self):
        return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def post_test(self, test_num):
        super(TcpTarget, self).post_test(test_num)
        if self.socket is not None:
            self.socket.close()
            self.socket = None

    def _send_to_target(self, data):
        self.socket.send(data)

    def _receive_from_target(self):
        try:
            return self.socket.recv(10000)
        except BaseException:
            return ""
