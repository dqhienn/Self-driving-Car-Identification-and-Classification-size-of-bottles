from board import SCL, SDA
import busio

# Import the PCA9685 module.
from adafruit_pca9685 import PCA9685
import adafruit_motor.servo

import time

class PCA9685_I2C():
    def __init__(self, ENA_Connec2PinPWM=0, IN1_Connec2PinPWM= 1, IN2_Connec2PinPWM= 2, Servo_Connec2Channel= 3):
        # Create the I2C bus interface.
        self.i2c_bus = busio.I2C(SCL, SDA)

        # Create a simple PCA9685 class instance.
        self.pca = PCA9685(self.i2c_bus)

        # Set the PWM frequency to 60hz.
        self.pca.frequency = 50

        # L298
        self.ENA = self.pca.channels[ENA_Connec2PinPWM] #connect PWM0 to pin ENA of L298
        self.IN1 = self.pca.channels[IN1_Connec2PinPWM] #connect PWM1 to pin IN1 of L298
        self.IN2 = self.pca.channels[IN2_Connec2PinPWM] #connect PWM2 to pin IN2 of L298

        # Servo
        self.servo_channel = self.pca.channels[Servo_Connec2Channel] #connect channel 3 to servo
        self.pca.frequency = 50
        self.servo = adafruit_motor.servo.Servo(self.servo_channel)

        self.dc_state = 0 # 0: stop state, 1: forwarding state, 2: backward state

    def DC_Forward(self, enablePWM=True):
        if self.dc_state == 0 or self.dc_state == 2:
            self.IN1.duty_cycle = 0xffff
            self.IN2.duty_cycle = 0
            if enablePWM:
                # for i in range(0xffff):
                for i in range(10000,0xffff,10000):
                    self.ENA.duty_cycle = i
                self.ENA.duty_cycle = 0xffff
            else:
                self.ENA.duty_cycle = 0xffff
            self.dc_state = 1

    def DC_Backward(self, enablePWM=True):
        if self.dc_state == 0 or self.dc_state == 1:
            self.IN1.duty_cycle = 0
            self.IN2.duty_cycle = 0xffff
            if enablePWM:
                # for i in range(0xffff):
                for i in range(10000,0xffff,10000):
                    self.ENA.duty_cycle = i
                self.ENA.duty_cycle = 0xffff
            else:
                self.ENA.duty_cycle = 0xffff
            self.dc_state = 2

    def DC_Stop(self, enablePWM=True):
        if self.dc_state == 1 or self.dc_state == 2:
            self.IN1.duty_cycle = 0
            self.IN2.duty_cycle = 0
            if enablePWM:
                # for i in range(0xffff, 0, -1):
                for i in range(0xffff,10000,-10000):
                    self.ENA.duty_cycle = i
                self.ENA.duty_cycle = 0
            else:
                self.ENA.duty_cycle = 0
            self.dc_state = 0

    def Servo_Angle(self,angle:int):
        self.servo.angle = angle

dc = PCA9685_I2C(ENA_Connec2PinPWM=0,
                  IN1_Connec2PinPWM=1,
                  IN2_Connec2PinPWM=2,
                  Servo_Connec2Channel=3)
dc.Servo_Angle(100)

# print("Run")
# # dc.DC_Stop(True)
# # time.sleep(2)
# dc.DC_Forward(True)
# # time.sleep(2)
# # dc.DC_Stop(True)
# # time.sleep(2)
# # dc.DC_Backward(True)
# time.sleep(2)
# dc.DC_Stop(True)
# # dc.Servo_Angle(90)
