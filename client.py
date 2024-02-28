import time
import socket
import busio
from board import SCL, SDA
from adafruit_pca9685 import PCA9685
import adafruit_motor.servo

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Initialize IP and PORT.")
client_socket.connect(('127.0.0.8', 12345))
client_socket.sendall('Connected'.encode('utf-8'))    # Send connected status
print("Connected to the server.")

class Control():
    def __init__(self, ENA=0, IN1=1, IN2=2, Servo1=3, Servo2=4):
        self.i2c_bus = busio.I2C(SCL, SDA)
        self.pca = PCA9685(self.i2c_bus)
        self.pca.frequency = 30  # Set the PWM frequency

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
        self.IN2.duty_cycle = int(0xffff * speed)
        self.IN1.duty_cycle = 0

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

def main():
    myControl = Control(ENA=0, IN1=1, IN2=2, Servo1=3, Servo2=4)
    myControl.Servo1_Angle(110)
    myControl.Servo2_Angle(30)
    id_stop = {0, 1, 2, 3, 4}  #['Saltshaker','Glue','Lifebuoy','7up','Pepsi']
    limits = {
        0: (480, 490),    # Saltshaker
        1: (485, 490),    # Glue
        2: (478, 490),    # Lifebuoy
        3: (360, 490),    # 7up
        4: (360, 490)     # Pepsi
    }
    flag = False
    response_str = []
    while True:
        myControl.Forward(True, speed=0.09)
        print("Forward")
        obj_stop_ids = []
        try:
            response = client_socket.recv(1024)
            response_str = response.decode('utf-8')
            if flag:
                print("Check flag = True")
                response_str = []
                flag = False
            else:
                print("response_str:", response_str)
                data = eval(response_str)
                print('eval: {}\n'.format(data))
        except Exception as e:
            print(f"Error response -> {e}")
            myControl.Stop(True)
            break
        if len(data) >= 2:
            obj, bottomLine = data[0], data[1]
            obj_stop_ids = list(set(obj).intersection(id_stop))
            
            if len(obj_stop_ids) >= 1:
                print("obj_stop_ids: ", obj_stop_ids)
                for id in obj_stop_ids:     #Lặp qua những phần tử trong danh sách
                    print("id: ", id)
                    print("len_obj: ", len(obj))
                    print("len_bottomLine: ", len(bottomLine))
                    #if len(obj) > 0 and len(bottomLine) > 0:
                    myControl.Servo2_Angle(180)
                    print("Servo2_Angle(180)")
                    if len(bottomLine) > 0:
                        if id in limits and id < len(bottomLine) and bottomLine[id] >= limits[id][0] and bottomLine[id] <= limits[id][1]:
                            flag = True
                            myControl.Stop(True)
                            print("Stoped")
                            time.sleep(3)
                            myControl.Servo2_Angle(30)
                            print("Servo2_Angle(30)")
                            time.sleep(2)
                            print("Picked up the object")
                            break
                continue
            elif response_str == 'Exit':
                print("Exit")
                myControl.Servo1_Angle(110)
                myControl.Servo2_Angle(30)
                myControl.Stop(True)
                client_socket.close()
                break
                
if __name__ == '__main__':
    main()