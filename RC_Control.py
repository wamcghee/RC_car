from MotorControl import *
from Server import *

IP_address = '192.168.1.89'
port = 9999

def timeout_func():
    drive.set_pwm(0)
    steering.set_pwm(0)
    print('Timeout reached.')

def data_func():
    str_data = data.split()
    drive_val = float(str_data[0])
    steer_val = float(str_data[1])
    drive.set_pwm(int(100*drive_val))
    steering.set_pwm(int(100*steer_val))

server = Server(port, IP_address, 1, data_func, 0.5, timeout_func)

while True:
	server.start_connection()
	while True:
		try:
			server.listen()
		except Exception as e:
			print(e)
			break

server.end_connection()