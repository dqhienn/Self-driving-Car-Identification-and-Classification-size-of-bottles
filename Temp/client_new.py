import time
import busio
import socket
from board import SCL, SDA
from adafruit_pca9685 import PCA9685
import adafruit_motor.servo

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Initialize IP and PORT.")
client_socket.connect(('127.0.0.1', 12345))
client_socket.sendall('Connected'.encode('utf-8'))    # Send connected status
print("Connected to the server.")

class Control:
    def __init__(self, ENA=0, IN1=1, IN2=2, Servo1=3, Servo2=4):
        self.i2c_bus = busio.I2C(SCL, SDA)
        self.pca = PCA9685(self.i2c_bus)
        self.pca.frequency = 30  # Set the PWM frequency

        self.ENA = self.pca.channels[ENA]
        self.IN1 = self.pca.channels[IN1]
        self.IN2 = self.pca.channels[IN2]

        self.servo1 = self.pca.channels[Servo1]
        self.servo2 = self.pca.channels[Servo2]
        self.servo1_instance = adafruit_motor.servo.Servo(self.servo1)
        self.servo2_instance = adafruit_motor.servo.Servo(self.servo2)

    def forward(self, enable_pwm=True, duty_cycle_step=1000, speed=1.0):
        if enable_pwm:
            for i in range(10000, 0xffff, duty_cycle_step):
                self.ENA.duty_cycle = int(i * speed)
            self.ENA.duty_cycle = int(0xffff * speed)
        else:
            self.ENA.duty_cycle = int(0xffff * speed)
        self.IN1.duty_cycle = 0
        self.IN2.duty_cycle = int(0xffff * speed)

    def backward(self, enable_pwm=True, duty_cycle_step=1000, speed=1.0):
        if enable_pwm:
            for i in range(10000, 0xffff, duty_cycle_step):
                self.ENA.duty_cycle = int(i * speed)
            self.ENA.duty_cycle = int(0xffff * speed)
        else:
            self.ENA.duty_cycle = int(0xffff * speed)
        self.IN1.duty_cycle = int(0xffff * speed)
        self.IN2.duty_cycle = 0

    def stop(self, enable_pwm=True):
        if enable_pwm:
            for i in range(0xffff, 10000, -10000):
                self.ENA.duty_cycle = i
            self.ENA.duty_cycle = 0
        else:
            self.ENA.duty_cycle = 0
        self.IN1.duty_cycle = 0
        self.IN2.duty_cycle = 0

    def servo1_angle(self, angle: int):
        self.servo1_instance.angle = angle

    def servo2_angle(self, angle: int):
        self.servo2_instance.angle = angle

def initialize_control():
    try:
        my_control = Control(ENA=0, IN1=1, IN2=2, Servo1=3, Servo2=4)
        my_control.servo1_angle(110)
        my_control.servo2_angle(30)
        return my_control
    except Exception as e:
        print("Error initializing control: {}".format(str(e)))
        return None

def handle_detection(my_control, obj, bottom_line, id_stop, limits):
    try:
        obj_stop_ids = list(set(obj).intersection(id_stop))
        if len(obj_stop_ids) >= 1:
            print("Mở góc kẹp 180 độ để chuẩn bị gắp vật")
            my_control.servo2_angle(180)
            for id in obj_stop_ids:
                if len(obj) > id and len(bottom_line) > id and id_stop and bottom_line[id] >= limits[id][0] and bottom_line[id] <= limits[id][1]:
                    print("Stopping -> Stop(True), Servo2_Angle(30)")
                    my_control.stop(True)
                    time.sleep(5)
                    my_control.servo2_angle(30)
            return True
    except Exception as e:
        print("Error handling detection: {}".format(str(e)))
        return False

def Run():
    try:
        my_control = initialize_control()
        if not my_control:
            return

        id_stop = {0, 1, 2, 3, 4}
        limits = {
            0: (478, 485),    # Saltshaker
            1: (478, 485),    # Glue
            2: (470, 475),    # Lifebuoy
            3: (470, 485),    # 7up
            4: (364, 475)     # Pepsi
        }

        while True:
            my_control.forward(True, speed=0.08)
            response = client_socket.recv(1024).decode('utf-8')

            if response == 'Exit':
                print("Exit -> Servo1_Angle(110), Servo2_Angle(30), Stop(True)")
                my_control.stop(True)
                my_control.servo1_angle(110)
                my_control.servo2_angle(30)
                client_socket.close()
                break

            data = eval(response)
            if data and len(data) >= 2:
                print("Check: len data >= 2")
                obj, bottom_line = data[0], data[1]
                print('Response: {}\n'.format(data))

                if not handle_detection(my_control, obj, bottom_line, id_stop, limits):
                    break

    except KeyboardInterrupt:
        print("KeyboardInterrupt: Closing connections and exiting...")
        time.sleep(1)
        client_socket.close()

if __name__ == '__main__':
    Run()
