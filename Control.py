import time
import busio
from board import SCL, SDA
from adafruit_pca9685 import PCA9685
import adafruit_motor.servo

class MyPCA9685():
    def __init__(self, ENA=0, IN1=1, IN2=2, Servo1=3, Servo2=4):
        self.i2c_bus = busio.I2C(SCL, SDA)
        self.pca = PCA9685(self.i2c_bus)
        self.pca.frequency = 50  # Set the PWM frequency to 50Hz.
        
        self.ENA = self.pca.channels[ENA]  # Connect PWM0 to pin ENA of L298
        self.IN1 = self.pca.channels[IN1]  # Connect PWM1 to pin IN1 of L298
        self.IN2 = self.pca.channels[IN2]  # Connect PWM2 to pin IN2 of L298
        
        self.servo1 = self.pca.channels[Servo1]  # Connect channel 3 to servo1
        self.servo2 = self.pca.channels[Servo2]  # Connect channel 4 to servo2

        self.servo1_instance = adafruit_motor.servo.Servo(self.servo1)
        self.servo2_instance = adafruit_motor.servo.Servo(self.servo2)

    def Backward(self, enablePWM=True, duty_cycle_step=1000, speed=1.0):
        if enablePWM:
            for i in range(10000, 0xffff, duty_cycle_step):
                self.ENA.duty_cycle = int(i * speed)
            self.ENA.duty_cycle = int(0xffff * speed)
        else:
            self.ENA.duty_cycle = int(0xffff * speed)
        self.IN1.duty_cycle = int(0xffff * speed)
        self.IN2.duty_cycle = 0

    def Forward(self, enablePWM=True, duty_cycle_step=1000, speed=1.0):
        if enablePWM:
            for i in range(10000, 0xffff, duty_cycle_step):
                self.ENA.duty_cycle = int(i * speed)
            self.ENA.duty_cycle = int(0xffff * speed)
        else:
            self.ENA.duty_cycle = int(0xffff * speed)
        self.IN1.duty_cycle = 0
        self.IN2.duty_cycle = int(0xffff * speed)

    def Stop(self, enablePWM=True):
        if enablePWM:
            for i in range(0xffff, 10000, -10000):
                self.ENA.duty_cycle = i
            self.ENA.duty_cycle = 0
        else:
            self.ENA.duty_cycle = 0

        self.IN1.duty_cycle = 0
        self.IN2.duty_cycle = 0

    def Servo1_Angle(self, angle: int):
        self.servo1_instance.angle = angle

    def Servo2_Angle(self, angle: int):
        self.servo2_instance.angle = angle

try:
    control = MyPCA9685(ENA=0, IN1=1, IN2=2, Servo1=3, Servo2=4)
    while True:
        #control.Forward(True, speed=0.2)

        control.Stop(True)

        #control.Backward(True, speed=0.2)

        control.Servo1_Angle(110)

        control.Servo2_Angle(30)	#MIN=30 | MAX=180 | 110

except KeyboardInterrupt:
    pass
