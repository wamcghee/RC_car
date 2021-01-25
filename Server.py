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
        self.display = ('New socket: ' + self.server_IP + '\n' +
        'Time: ' + time.asctime(time.localtime(time.time())) + '\n')
        self.data_func = data_func
        self.timeout = timeout
        self.timeout_func = timeout_func

    def start_connection(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind((self.server_IP, self.port))
            self.socket.listen(self.backlog)
            #self.listen()
            self.client, self.client_address = self.socket.accept()
            self.connected = True
            self.t_last = time.time()
            self.display = ('Connection made.\n' +
            'Time: ' + time.asctime(time.localtime(time.time())) + '\n')
        except Exception as e:
            self.display = ('Error in connection.\n' + str(e) + '\n' + 
            'Time: ' + time.asctime(time.localtime(time.time())) + '\n')

    def end_connection(self):
        self.socket.close()
        self.connected = False
        self.display = ('Connection ended.\n' +
        'Time: ' + time.asctime(time.localtime(time.time())) + '\n')

    def listen(self):
        data = self.client.recv(1024).decode()
        if data and bool(self.data_func):
            if data == 'exit':
                self.end_connection()
            self.data_func(data)
            self.t_last = time.time()
            self.display = 'Transmission recieved.\n'
        elif time.time() - self.t_last > self.timeout:
            if self.timeout_func: self.timeout_func()
            self.display = 'Transmission timed out.\n'