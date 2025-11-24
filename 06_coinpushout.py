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


def move_with_ramp(target: float, current: float, ramp_step: float | None, ramp_delay: float) -> float:
    """角度をランプ移動で target へ。ramp_step が None の場合は即移動。"""
    if ramp_step is None:
        servo.angle = target
        return target
    # 方向決定
    step = ramp_step if target > current else -ramp_step
    a = current
    # 少しずつ移動
    while (step > 0 and a < target) or (step < 0 and a > target):
        a += step
        # オーバーシュート補正
        if (step > 0 and a > target) or (step < 0 and a < target):
            a = target
        servo.angle = a
        sleep(ramp_delay)
    return target


def run(angle1: float, angle2: float, wait_time: float, loops: int | None, ramp_step: float | None, ramp_delay: float):
    count = 0
    print(
        f"開始: angle1={angle1}, angle2={angle2}, wait={wait_time}s, "
        f"loops={'infinite' if loops is None else loops}, ramp_step={ramp_step}, ramp_delay={ramp_delay}s"
    )
    try:
        current = servo.angle if servo.angle is not None else angle1
        # 初期位置へ
        current = move_with_ramp(angle1, current, ramp_step, ramp_delay)
        sleep(wait_time)
        if loops is None:
            while True:
                print(f"Angle: {angle1}")
                current = move_with_ramp(angle1, current, ramp_step, ramp_delay)
                sleep(wait_time)

                print(f"Angle: {angle2}")
                current = move_with_ramp(angle2, current, ramp_step, ramp_delay)
                sleep(wait_time)
        else:
            for _ in range(loops):
                count += 1
                print(f"[Loop {count}/{loops}] Angle: {angle1}")
                current = move_with_ramp(angle1, current, ramp_step, ramp_delay)
                sleep(wait_time)

                print(f"[Loop {count}/{loops}] Angle: {angle2}")
                current = move_with_ramp(angle2, current, ramp_step, ramp_delay)
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


def positive_float(value: str) -> float:
    v = float(value)
    if v <= 0:
        raise argparse.ArgumentTypeError("正の正数を指定してください")
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
    parser.add_argument(
        "--ramp-step",
        "-rs",
        type=positive_float,
        default=None,
        help="ランプ移動時のステップ角度(度)。指定なしで即移動。例: 2",
    )
    parser.add_argument(
        "--ramp-delay",
        "-rd",
        type=positive_float,
        default=0.02,
        help="ランプ移動ステップ間の待ち秒(既定: 0.02)",
    )

    args = parser.parse_args()

    if args.angle1 == args.angle2:
        parser.error("angle1 と angle2 が同じです。異なる角度を指定してください。")

    run(args.angle1, args.angle2, args.wait, args.loops, args.ramp_step, args.ramp_delay)
