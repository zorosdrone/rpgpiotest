from gpiozero import AngularServo
from time import sleep

# GPIO 18番ピン（物理ピン 12番）を使用。
# SG90などのマイクロサーボ向けにパルス幅を設定しています。
# servo = AngularServo(ピン番号, min_pulse_width=最小パルス幅, max_pulse_width=最大パルス幅)
servo = AngularServo(18, min_pulse_width=0.0005, max_pulse_width=0.0024)

try:
    while True:
        # --- 動作範囲のテスト ---
        
        # 1. 中央 (90度)
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