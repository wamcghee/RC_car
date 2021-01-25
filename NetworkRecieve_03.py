from Server import *
from MotorControl import *

host_Address = '192.168.1.89'
port = 9999
backlog = 1
size = 1024

def timeout_func():
    drive.set_pwm(0)
    steering.set_pwm(0)

def data_func(data):
    str_data = data.split()
    drive_val = float(str_data[0])
    steer_val = float(str_data[1])
    drive.set_pwm(int(100*drive_val))
    steering.set_angle(int(-90*steer_val))

server = Server(port, host_Address, 1, data_func, 0.5, timeout_func)


while True:
    server = Server(port, host_Address, backlog, data_func, 0.5, timeout_func)
    server.start_connection()
    while True:
        server.listen()
    server.end_connection()

drive.set_pwm(0)
steering.set_angle(0)
GPIO.cleanup()
s.close()