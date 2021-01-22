import time
import RPi.GPIO as GPIO

GPIO.cleanup()

GPIO.setmode(GPIO.BCM)
 
class StepperMotor:
    '''
    Controls and keeps data on 28BYJ-48 stepper motor.
    '''

    def __init__(self, pin1, pin2, pin3, pin4, start_angle = 0.0):
        # Initialize pin locations and settings
        self.pins = [pin1, pin2, pin3, pin4] # Array of pin numbers on Raspberry Pi board
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT) # Set pins to be output
            GPIO.output(pin, False) # Set pins to 0 V.

        self.position = start_angle # Tracks the position of the motor shaft.

        self.substeps = 8 # Number of substeps in one full motor step
        self.Seq = [[] for i in range(self.substeps)] # Array of pin states for each substep.
        # 1 for pin on and 0 for pin off.
        self.Seq[0] = [1,0,0,0]
        self.Seq[1] = [1,1,0,0]
        self.Seq[2] = [0,1,0,0]
        self.Seq[3] = [0,1,1,0]
        self.Seq[4] = [0,0,1,0]
        self.Seq[5] = [0,0,1,1]
        self.Seq[6] = [0,0,0,1]
        self.Seq[7] = [1,0,0,1]
    
    # Directions are defined looking at the casing of the motor with the label.
    # left is ccw when viewed from the label and right is cw when viewed from the label.

    
    def left(self, angle, speed = 90.0):
        '''
        angle:  Degrees to turn the shaft
        speed:  Amgular velocity of shaft in degrees/s

        Rotates the shaft of the motor left the specified angle at the specified speed.
        '''
        steps = int(512 * angle / 360) # Number of steps the motor must complete to turn the shaft the desired amount
        WaitTime = 360 / (512 * speed) # Dead time between steps to achieve desired speed

        # Loop through the number of steps required
        for s in range(steps):
            # Loop through the substeps for each step
            for step in range(8):
                v = self.Seq[step] # Vector of pin values
                # Loop through the pins to set their states
                for i in range(4):
                    pin = self.pins[i]
                    if v[i] == 0:
                        GPIO.output(pin, False)
                    else:
                        GPIO.output(pin, True)
                time.sleep(WaitTime/8) # Wait after the step
                self.position = (self.position + 360/512/8) % 360 # Update the position variable


    def right(self, angle, speed = 90.0):
        '''
        angle:  Degrees to turn the shaft
        speed:  Amgular velocity of shaft in degrees/s

        Rotates the shaft of the motor right the specified angle at the specified speed.
        '''
        steps = int(512 * angle / 360) # Number of steps the motor must complete to turn the shaft the desired amount
        WaitTime = 360 / (512 * speed) # Dead time between steps to achieve desired speed

        # Loop through the number of steps required
        for s in range(steps):
            # Loop through the substeps for each step
            for step in range(7, -1, -1):
                v = self.Seq[step] # Vector of pin values
                # Loop through the pins to set their states
                for i in range(4):
                    pin = self.pins[i]
                    if v[i] == 0:
                        GPIO.output(pin, False)
                    else:
                        GPIO.output(pin, True)
                time.sleep(WaitTime/8) # Wait after the step
                self.position = (self.position + 360/512/8) % 360 # Update the position variable

    
    def turn_to_angle(self, new_pos, speed = 90.0, direction = 'fastest'):
        '''
        new_pos:    The desired position of the shaft in degrees
        speed:      The desired speed of rotation in degrees/s
        direction:  The direction of rotation. 'left' and 'right' use their respective
                    directiona and 'fastest' selects the shorter rotation of the two.

        Rotates the motor shaft to the desired position from the current position
        in the indicated direction and speed.
        '''
        # Find speeds for left and right rotations
        new_pos = new_pos % 360.0
        angle_left = new_pos - self.position
        if angle_left < 0: angle_left = angle_left + 360 # Account for negative values
        angle_right = self.position - new_pos
        if angle_right < 0: angle_right = angle_right + 360 # Account for negative values
        # If 'fastest' is selected, pick the faster direction
        if direction == 'fastest':          
            if angle_right < angle_left:
                direction = 'right'
            else:
                direction = 'left'
        # Execute the rotation for the selected direction
        if direction == 'right':
            self.right(angle_right, speed)
        elif direction == 'left':
            self.left(angle_left, speed)
    
    def reassign_position(self, position):
        '''
        position: Value to which to change the motor's position variable

        Changes the motor position variable to the given value without moving the motor.
        This function is useful for calibrations so that the motor setpoints allign with
        the physical system around the motor.
        '''
        self.position = position



class ServoMotor:
    '''
    Control a servo motor with PWM input.
    '''

    def __init__(self, pwm_pin, angle = 0, offset = 90, f_pwm = 50, dc_min = 5, angle_min = 0, dc_max = 10, angle_max = 180):
        self.pwm_pin = pwm_pin
        self.f_pwm = f_pwm
        self.dc_min = dc_min
        self.dc_max = dc_max
        self.angle_min = angle_min
        self.angle_max = angle_max
        self.offset = offset
        self.angle = angle

        # Setup PWM
        GPIO.setup(self.pwm_pin, GPIO.OUT) # Set pwm pin to be output
        self.pwm = GPIO.PWM(self.pwm_pin, self.f_pwm) # Set pwm frequency
        self.pwm.start(self.dc_min + (self.angle + self.offset - self.angle_min) / (self.dc_mac - self.dc_min)) # set duty cycle

    def set_angle(angle):
        if angle < 0: angle = 0
        elif angle > 180: angle = 180
        self.pwm.ChangeDutyCycle(self.dc_min + (angle + self.offset - self.angle_min) / (self.dc_mac - self.dc_min))
        self.angle = angle



class DCMotorWithEncoder:
    '''
    Control and keep data from a DC motor with PWM speed control and 2-wire encoder.
    '''
    
    def __init__(self, pwm_pin, in_1, in_2, encoder_1, encoder_2, ratio = 750, angle = 0):
        self.motor = DCMotor(pwm_pin, in_1, in_2)
        self.encoder = Encoder(encoder_1, encoder_2)

    def encoder_pulse(self, x):
        '''
        Increment encoder position when interrupt pin changes.
        '''
        self.encoder.encoder_pulse(x)

    def set_pwm(self, p):
        '''
        Set the motor direction and PWM duty cycle.

        p: int -100 to 100. If p < 0, direction is reversed.
           abs(p) is percent duty cycle.
        '''
        self.motor.set_pwm(p)



class DCMotor:
    '''
    Control a DC motor with PWM speed control using L298N motor controller.
    '''
    
    def __init__(self, pwm_pin, in_1, in_2):
        self.pwm_pin = pwm_pin
        self.in_1 = in_1
        self.in_2 = in_2
        
        # Setup PWM
        GPIO.setup(self.pwm_pin, GPIO.OUT) # Set pwm pin to be output
        self.pwm = GPIO.PWM(self.pwm_pin, 100) # Set pwm frequency to 100 Hz
        self.pwm.start(0) # set duty cycle to 0, range 0 to 100
        
        # Setup input pins
        GPIO.setup(self.in_1, GPIO.OUT)
        GPIO.output(self.in_1, False)
        GPIO.setup(self.in_2, GPIO.OUT)
        GPIO.output(self.in_2, False)

    def set_pwm(self, p):
        '''
        Set the motor direction and PWM duty cycle.

        p: int -100 to 100. If p < 0, direction is reversed.
           abs(p) is percent duty cycle.
        '''
        if p > 0:
            GPIO.output(self.in_1, True)
            GPIO.output(self.in_2, False)
            self.pwm.ChangeDutyCycle(p)
        else:
            GPIO.output(self.in_1, False)
            GPIO.output(self.in_2, True)
            self.pwm.ChangeDutyCycle(-p)

class Encoder:
    '''
    Keep data from a bipolar encoder
    '''

    def __init__(self, encoder_1, encoder_2, ratio = 750, angle = 0):
        self.encoder_1 = encoder_1
        self.encoder_2 = encoder_2
        self.ratio = ratio
        self.angle = angle
        self.speed = 0
        self.dir = True
        self.e1_last = True

        # Setup encoder pins
        GPIO.setup(self.encoder_1, GPIO.IN, pull_up_down=GPIO.PUD_UP) # Interrupt pin
        GPIO.add_event_detect(self.encoder_1, GPIO.BOTH, callback = self.encoder_pulse)
        GPIO.setup(self.encoder_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def encoder_pulse(self, x):
        '''
        Increment encoder position when interrupt pin changes.
        '''

        e1_val = GPIO.input(self.encoder_1)
        if not self.e1_last and e1_val:
            e2_val = GPIO.input(self.encoder_2)
            if not e2_val and self.dir:
                self.dir = False
            elif e2_val and not self.dir:
                self.dir = True
        self.e1_last = e1_val
        if self.dir:
            self.angle = self.angle + 1/self.ratio
        else:
            self.angle = self.angle - 1/self.ratio

#steering = DCMotor(23, 22, 27)
steering = ServoMotor(12)
drive = DCMotor(15, 18, 17)
left_encoder = Encoder(24, 10)
right_encoder = Encoder(9, 11)

# Servo PWM is 12