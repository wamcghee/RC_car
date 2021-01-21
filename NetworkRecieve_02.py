import socket
import time
from MotorControl import *

host_Address = '192.168.1.89'
port = 9999
backlog = 1
size = 1024

while True:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host_Address, port))
    s.listen(backlog)

    client, address = s.accept()
    t_last = time.time()

    while True:
        data = client.recv(size).decode()
        if data:
            print(data)
            str_data = data.split()
            drive_val = float(str_data[0])
            steer_val = float(str_data[1])
            drive.set_pwm(int(100*drive_val))
            steering.set_pwm(int(100*steer_val))
            t_last = time.time()
            #client.send(data)
        elif time.time() - t_last > 0.5:
            #print('Timed out')
            drive.set_pwm(0)
            steering.set_pwm(0)
            break
    s.close()


drive.set_pwm(0)
steering.set_pwm(0)
GPIO.cleanup()
s.close()