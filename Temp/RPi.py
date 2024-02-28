import time
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

class Motor():
    def __init__(self, ENA, IN1, IN2):
        self.ENA = ENA
        self.IN1 = IN1
        self.IN2 = IN2
        GPIO.setup(self.ENA, GPIO.OUT)
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)

        self.pwm = GPIO.PWM(self.ENA, 500)
        self.pwm.start(0)  # Khởi động PWM với duty cycle ban đầu là 0%

    def forward(self, DC):
        print("Forward")
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        self.pwm.ChangeDutyCycle(DC)

    def backward(self, DC):
        print("Backward")
        GPIO.output(self.IN1, GPIO.HIGH)
        GPIO.output(self.IN2, GPIO.LOW)
        self.pwm.ChangeDutyCycle(DC)

    def stop(self):
        print("STOP")
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.LOW)
        self.pwm.ChangeDutyCycle(0)  # Tắt PWM

try:
    motor = Motor(15, 31, 33)

    while True:
        motor.forward(50)  # Chạy tiến với tốc độ 50% công suất
        time.sleep(10)  # Giữ tốc độ không đổi trong 2 giây

        motor.backward(30)  # Chạy lùi với tốc độ 30% công suất
        time.sleep(10)  # Giữ tốc độ không đổi trong 2 giây

        motor.stop()  # Dừng động cơ
        time.sleep(5)  # Nghỉ 2 giây trước khi lặp lại

except KeyboardInterrupt:
    pass

motor.pwm.stop()
GPIO.cleanup()
