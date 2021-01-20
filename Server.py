import socket
import time

class Server:

    def __init__(self, port, IP, backlog = 1, data_func = False, timeout = 0.5, timeout_func = None):
        self.port = port
        self.server_IP = IP
        self.backlog = backlog
        self.t_last = time.time()
        self.connected = False
        self.client = None
        self.client_address = None

    def start_connection(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind((self.server_IP, self.port))
            self.socket.listen()
            self.connected = True
            self.listen()
            self.client, self.address = socket.accept()
            self.t_last = time.time()
        except Exception as e:
            print('Error in connection')
            print(e)

    def end_connection(self):
        self.socket.close()
        self.connected = False

    def listen(self):
        data = self.client.recv(1024).decode()
        if data and bool(data_func()):
            if data == 'exit':
                self.end_connection()
            data_func(data)
            self.t_last = time.time()
        elif time.time() - self.t_last > timeout:
            timeout_func()