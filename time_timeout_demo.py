import time

from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory


SERVO_PIN = 18


def move_servo_with_timeout(
    servo: AngularServo,
    target_angle: float,
    ramp_step: float,
    ramp_delay: float,
    factor: float = 2,
) -> None:
    """サーボを現在角度から target_angle までランプ移動し、
    理論時間×factor を超えたらタイムアウトとして停止するデモ。

    ※サーボからは実位置は読めないので、あくまで「時間ルール」で止めるだけ。
    """

    current = servo.angle if servo.angle is not None else 0.0
    delta = abs(target_angle - current)
    steps = max(1, int(delta / ramp_step))
    theoretical = steps * ramp_delay
    # 実験用に「かなり厳しい」タイムアウトにする: 理論時間の半分
    timeout = theoretical * 0.5

    print("=== move_servo_with_timeout ===")
    print(f"current={current:.1f}, target={target_angle:.1f}, delta={delta:.1f}")
    print(f"ramp_step={ramp_step}deg, ramp_delay={ramp_delay}s")
    print(f"理論時間={theoretical:.3f}s, タイムアウト(理論×0.5)={timeout:.3f}s\n")

    start_t = time.monotonic()
    angle = current
    step = ramp_step if target_angle > current else -ramp_step

    for i in range(steps):
        elapsed = time.monotonic() - start_t
        if elapsed > timeout:
            print(f"[TIMEOUT] 経過{elapsed:.3f}s > timeout{timeout:.3f}s → サーボ解放して停止")
            servo.detach()
            return

        angle += step
        # オーバーシュート防止
        if (step > 0 and angle > target_angle) or (step < 0 and angle < target_angle):
            angle = target_angle

        servo.angle = angle
        print(f"[STEP {i}] angle={angle:.1f}, 経過{elapsed:.3f}s")
        time.sleep(ramp_delay)

    elapsed = time.monotonic() - start_t
    print(f"完了: angle={angle:.1f}, 経過{elapsed:.3f}s (timeout{timeout:.3f}s 以下)\n")


if __name__ == "__main__":
    print("pigpiod が動いていることを確認してください (sudo systemctl status pigpiod)")

    factory = PiGPIOFactory()
    servo = AngularServo(
        SERVO_PIN,
        min_angle=0,
        max_angle=180,
        min_pulse_width=0.0005,
        max_pulse_width=0.0024,
        pin_factory=factory,
    )

    try:
        # 例1: 0→180度へ、理論時間内に収まる設定
        move_servo_with_timeout(servo, target_angle=180, ramp_step=5.0, ramp_delay=0.02, factor=2.0)

        time.sleep(1.0)

        # 例2: わざと ramp_delay を大きくして、タイムアウトを狙う設定
        move_servo_with_timeout(servo, target_angle=0, ramp_step=5.0, ramp_delay=0.6, factor=1.2)

    except KeyboardInterrupt:
        print("\nユーザーによる中断")
    finally:
        try:
            servo.detach()
        except Exception:
            pass
