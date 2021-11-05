from MotorControl import *
from Server import *
import numpy as np
import cv2
import matplotlib.pyplot as plt

# Internet information
IP_address = '192.168.1.89'
port = 9999

# Camera information
cam_port = 0
cam = cv2.VideoCapture(cam_port)
resize_factor = 4
global take_image
image = None

def timeout_func():
    drive.set_pwm(0)
    steering.set_pwm(0)
    print('Timeout reached.')

def data_func():
    str_data = data.split()
    drive_val = float(str_data[0])
    steer_val = float(str_data[1])
    take_image = float(str_data[2])
    g.set_pwm(int(100*drive_val))
    steering.set_pwm(int(100*steer_val))
    if take_image:
        result, image = cam.read()
        shape = (int(image.shape[1] / resize_factor), int(image.shape[0] / resize_factor))


server = Server(port, IP_address, 1, data_func, 0.5, timeout_func)

while True:
    server.start_connection()
    image = None
    while True:
        # Recieve data
        try:
            server.listen()
        except Exception as e:
            print(e)
            break
        # Send data
        if image != None:
            try:
                server.send(image.tobytes())
                image = None
            except Exception as e:
                print(e)
                break

drive.set_pwm(0)
steering.set_pwm(0)
GPIO.cleanup()
server.end_connection()