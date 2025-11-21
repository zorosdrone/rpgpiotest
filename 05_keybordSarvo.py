#!/usr/bin/env python3
"""
05_keybordSarvo.py

キーボードの左右キー（または a/d）でサーボ角度を制御します。

使用方法:
  1) Raspberry Pi 上で pigpiod を起動:
       sudo systemctl start pigpiod
  2) 仮想環境を使っている場合は有効化:
       source venv/bin/activate
  3) スクリプトを実行:
       python3 05_keybordSarvo.py

操作:
  ← or a : サーボを左へ（角度を減らす）
  → or d : サーボを右へ（角度を増やす）
  s       : 角度を 0 に戻す
  q or Ctrl-C : 終了

注意:
  - pigpiod が起動していないと接続に失敗します。
  - サーボの配線と電源は安全に行ってください。
"""

import sys
import termios
import tty
import time
import os
import signal

from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory

# 設定
SERVO_PIN = 18          # PWM 出力に使う GPIO 番号
MIN_ANGLE = -90
MAX_ANGLE = 90
STEP = 5                # 1回のキー入力で変化する角度（度）
INITIAL_ANGLE = 0


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def get_key():
    """端末から1文字または矢印シーケンスを読み取る。"""
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch1 = sys.stdin.read(1)
        if ch1 == "\x1b":
            # エスケープシーケンス（矢印キーなど）
            ch2 = sys.stdin.read(1)
            ch3 = sys.stdin.read(1)
            return ch1 + ch2 + ch3
        else:
            return ch1
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def print_instructions(angle):
    os.system('printf "\033c"')  # 画面クリア（端末互換）
    print("Keyboard Servo Control")
    print("----------------------")
    print("Controls: ← / a = left  | → / d = right | s = center | q = quit")
    print()
    print(f"Current angle: {angle}°")
    print()
    print("※ Ctrl+C でも終了できます")


def main():
    # pigpio factory とサーボ初期化
    try:
        factory = PiGPIOFactory()
        servo = AngularServo(SERVO_PIN, min_pulse_width=0.0005, max_pulse_width=0.0025, pin_factory=factory)
    except Exception as e:
        print("--- 🚨 pigpio 接続エラー 🚨 ---")
        print("pigpiod が起動していない、または接続に失敗しました。")
        print("ターミナルで 'sudo systemctl start pigpiod' を実行してから再度実行してください。")
        print(f"詳細: {e}")
        sys.exit(1)

    angle = INITIAL_ANGLE
    servo.angle = angle

    # Ctrl+C を graceful に処理
    def handler(signum, frame):
        raise KeyboardInterrupt

    signal.signal(signal.SIGINT, handler)

    try:
        print_instructions(angle)
        while True:
            key = get_key()
            changed = False

            # 矢印キーはエスケープシーケンス
            if key == '\x1b[D' or key == 'a':  # 左
                angle = clamp(angle - STEP, MIN_ANGLE, MAX_ANGLE)
                changed = True
            elif key == '\x1b[C' or key == 'd':  # 右
                angle = clamp(angle + STEP, MIN_ANGLE, MAX_ANGLE)
                changed = True
            elif key == 's':
                angle = 0
                changed = True
            elif key == 'q':
                break
            else:
                # 未処理のキーは無視
                continue

            if changed:
                try:
                    servo.angle = angle
                except Exception as e:
                    print(f"サーボ制御エラー: {e}")
                print_instructions(angle)

            # 過負荷防止
            time.sleep(0.05)

    except KeyboardInterrupt:
        print('\n終了します...')

    finally:
        try:
            servo.close()
        except:
            pass
        # 端末が壊れる場合があるので改行
        print('Goodbye')


if __name__ == '__main__':
    main()
