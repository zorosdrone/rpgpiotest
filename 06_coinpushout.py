import argparse
from time import sleep

from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory


# --- 固定設定 ---
SERVO_PIN = 18  # ラズパイのGPIOピン番号

# pigpioデーモンを利用してジッターを防止
factory = PiGPIOFactory()

# サーボの設定 (SG90などの一般的なサーボに合わせてパルス幅を調整)
# min_pulse_width=0.0005 (0.5ms), max_pulse_width=0.0024 (2.4ms) はSG90の典型値
servo = AngularServo(
    SERVO_PIN,
    min_angle=0,
    max_angle=180,
    min_pulse_width=0.0005,
    max_pulse_width=0.0024,
    pin_factory=factory,
)


def run(angle1: float, angle2: float, wait_time: float, loops: int | None):
    count = 0
    print(f"開始: angle1={angle1}, angle2={angle2}, wait={wait_time}s, loops={'infinite' if loops is None else loops}")
    try:
        if loops is None:
            while True:
                print(f"Angle: {angle1}")
                servo.angle = angle1
                sleep(wait_time)

                print(f"Angle: {angle2}")
                servo.angle = angle2
                sleep(wait_time)
        else:
            for _ in range(loops):
                count += 1
                print(f"[Loop {count}/{loops}] Angle: {angle1}")
                servo.angle = angle1
                sleep(wait_time)

                print(f"[Loop {count}/{loops}] Angle: {angle2}")
                servo.angle = angle2
                sleep(wait_time)
    except KeyboardInterrupt:
        print("\n停止しました (Ctrl+C)")
    finally:
        try:
            servo.detach()
        except Exception:
            pass


def positive_int(value: str) -> int:
    iv = int(value)
    if iv <= 0:
        raise argparse.ArgumentTypeError("正の整数を指定してください")
    return iv


def angle_type(value: str) -> float:
    v = float(value)
    if not (0 <= v <= 180):
        raise argparse.ArgumentTypeError("角度は0〜180の範囲で指定してください")
    return v


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="サーボを angle1 と angle2 の間で往復させます。"
    )
    parser.add_argument("--angle1", "-a1", type=angle_type, default=20, help="開始角度 (0-180, 既定: 20)")
    parser.add_argument("--angle2", "-a2", type=angle_type, default=175, help="終了角度 (0-180, 既定: 175)")
    parser.add_argument("--wait", "-w", type=float, default=3.0, help="各移動後の待ち時間(秒) (既定: 3.0)")
    parser.add_argument(
        "--loops",
        "-l",
        type=positive_int,
        default=None,
        help="往復ループ回数。指定しない場合は無限ループ。",
    )

    args = parser.parse_args()

    if args.angle1 == args.angle2:
        parser.error("angle1 と angle2 が同じです。異なる角度を指定してください。")

    run(args.angle1, args.angle2, args.wait, args.loops)
