from gpiozero import AngularServo
from time import sleep  

from gpiozero.pins.pigpio import PiGPIOFactory
factory = PiGPIOFactory()

servo = AngularServo(18, min_pulse_width=0.5/1000,
                      max_pulse_width=2.5/1000,
                      pin_factory=factory)

try:
    while True:
        # 1. 中央 (0度)
        print("中央 (0度) に設定")
        servo.angle = 0
        sleep(1)
        
        # 2. 右端 (90度)
        print("右端 (90度) に設定")
        servo.angle = 90
        sleep(1)
        
        # 3. 左端 (-90度)
        # print("左端 (-90度) に設定")
        # servo.angle = -90
        # sleep(1)

except KeyboardInterrupt:
        print("\nプログラムを終了し、サーボを解放します。")
finally:
    # プログラム終了時、サーボ信号を停止します
    servo.close()       