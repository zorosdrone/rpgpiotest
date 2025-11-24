import argparse
from time import sleep, monotonic

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


def move_with_ramp(
    target: float,
    current: float,
    ramp_step: float | None,
    ramp_delay: float,
    stuck_threshold: float,
    stuck_max_steps: int,
) -> float:
    """角度をランプ移動で target へ。

    - ramp_step が None の場合は即移動。
        - 連続して角度変化が stuck_threshold 未満のステップが
            stuck_max_steps 回続いたら機械的噛み込みとみなし KeyboardInterrupt を送出。
    """
    if ramp_step is None:
        servo.angle = target
        return target

    step = ramp_step if target > current else -ramp_step
    a = current
    prev_a = a
    stuck_count = 0

    # 理論上の移動時間からタイムアウト(安全係数2倍)を自動計算
    total_delta = abs(target - current)
    if ramp_step > 0:
        steps = max(1, int(total_delta / ramp_step))
    else:
        steps = 1
    theoretical_time = steps * ramp_delay
    move_timeout = theoretical_time * 2.0
    start_t = monotonic()

    while (step > 0 and a < target) or (step < 0 and a > target):
        if monotonic() - start_t > move_timeout:
            print("移動タイムアウト: 想定時間の2倍を超えたためサーボを解放します")
            servo.detach()
            raise KeyboardInterrupt
        a += step
        # オーバーシュート補正
        if (step > 0 and a > target) or (step < 0 and a < target):
            a = target

        servo.angle = a
        # 実質的に動いていないかチェック
        if abs(a - prev_a) < stuck_threshold:
            stuck_count += 1
            if stuck_count >= stuck_max_steps:
                print("警告: サーボが機械的に噛み込んだ可能性があるため停止します")
                raise KeyboardInterrupt
        else:
            stuck_count = 0

        prev_a = a
        sleep(ramp_delay)

    return target


def run(
    angle1: float,
    angle2: float,
    wait_time: float,
    loops: int | None,
    ramp_step: float | None,
    ramp_delay: float,
    stuck_threshold: float,
    stuck_max_steps: int,
):
    count = 0
    print(
        f"開始: angle1={angle1}, angle2={angle2}, wait={wait_time}s, "
        f"loops={'infinite' if loops is None else loops}, ramp_step={ramp_step}, ramp_delay={ramp_delay}s, "
        f"stuck_threshold={stuck_threshold}, stuck_max_steps={stuck_max_steps}"
    )
    try:
        current = servo.angle if servo.angle is not None else angle2
        # 初期位置へ（angle2 側に合わせる）
        current = move_with_ramp(angle2, current, ramp_step, ramp_delay, stuck_threshold, stuck_max_steps)
        sleep(wait_time)
        if loops is None:
            while True:
                print(f"Angle: {angle2}")
                current = move_with_ramp(angle2, current, ramp_step, ramp_delay, stuck_threshold, stuck_max_steps)
                sleep(wait_time)
                print(f"Angle: {angle1}")
                current = move_with_ramp(angle1, current, ramp_step, ramp_delay, stuck_threshold, stuck_max_steps)
                sleep(wait_time)
        else:
            for _ in range(loops):
                count += 1
                print(f"[Loop {count}/{loops}] Angle: {angle2}")
                current = move_with_ramp(angle2, current, ramp_step, ramp_delay, stuck_threshold, stuck_max_steps)
                sleep(wait_time)

                print(f"[Loop {count}/{loops}] Angle: {angle1}")
                current = move_with_ramp(angle1, current, ramp_step, ramp_delay, stuck_threshold, stuck_max_steps)
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
        default=1,
        help="往復ループ回数。指定しない場合は1回のみ。",
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
    parser.add_argument(
        "--stuck-threshold",
        type=positive_float,
        default=0.1,
        help="機械的噛み込み検出用の最小有効角度変化(度) (既定: 0.1)",
    )
    parser.add_argument(
        "--stuck-max-steps",
        type=positive_int,
        default=10,
        help="上記しきい値未満の変化が連続した場合に停止するステップ数 (既定: 10)",
    )

    args = parser.parse_args()

    if args.angle1 == args.angle2:
        parser.error("angle1 と angle2 が同じです。異なる角度を指定してください。")

    run(
        args.angle1,
        args.angle2,
        args.wait,
        args.loops,
        args.ramp_step,
        args.ramp_delay,
        args.stuck_threshold,
        args.stuck_max_steps,
    )
