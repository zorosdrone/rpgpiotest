from gpiozero import AngularServo
from time import sleep

from gpiozero.pins.pigpio import PiGPIOFactory


# --- 設定 ---
SERVO_PIN = 18       # Arduinoの「9」に相当。ラズパイのGPIOピン番号（以前と同じなら18）
WAIT_TIME = 3      # Arduinoの「3000」(ms)に相当。Pythonは秒単位なので 3 (s)

# pigpioデーモンを利用してジッターを防止
factory = PiGPIOFactory()# サーボの設定 (SG90などの一般的なサーボに合わせてパルス幅を調整済み)
# min_pulse_width=0.0005 (0.5ms), max_pulse_width=0.0024 (2.4ms) はSG90の典型値
servo = AngularServo(SERVO_PIN, min_angle=0, max_angle=180,
                     min_pulse_width=0.0005, max_pulse_width=0.0024,
                     pin_factory=factory)

def loop():
    while True:
        # 0度へ移動 (Arduino: myservo.write(0))
        print("Angle: 0")
        servo.angle = 0
        sleep(WAIT_TIME)  # Arduino: delay(speed)

        # 180度へ移動 (Arduino: myservo.write(180))
        print("Angle: 180")
        servo.angle = 180
        sleep(WAIT_TIME)  # Arduino: delay(speed)

if __name__ == "__main__":
    try:
        print("サーボ制御を開始します (Ctrl+Cで停止)")
        loop()
    except KeyboardInterrupt:
        print("\n停止しました")
        servo.detach() # サーボの制御を解放
