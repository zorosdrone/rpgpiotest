#動かないのであきらめる編集テスト

from gpiozero import LED
from time import sleep

# "ACT"を指定すると本体のアクセスランプが制御対象になります
# led = LED("ACT")
led = LED(27)

print("本体のランプを見ててください...")

while True:
    led.on()   # 点灯
    sleep(0.5)
    led.off()  # 消灯
    sleep(0.5)
