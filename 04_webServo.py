from flask import Flask, render_template_string, request
from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
import os
import sys

# pigpioデーモンが起動していることを前提とします
# (venv_flask) の環境では os.environ で factory を設定する必要があります
try:
    factory = PiGPIOFactory()
    # GPIO 18番ピン, ジッター解消のためpigpio Factoryを使用
    servo = AngularServo(18, min_pulse_width=0.0005, max_pulse_width=0.0024, pin_factory=factory)
except Exception as e:
    # pigpiodが起動していない、または接続できない場合の処理
    print("--- 🚨 エラー 🚨 ---")
    print("pigpiod (pigpioデーモン) が起動していません。")
    print("ターミナルで [ sudo pigpiod ] を実行してから、再度プログラムを起動してください。")
    print(f"詳細: {e}", file=sys.stderr)
    sys.exit(1)


app = Flask(__name__)

# --- HTMLテンプレート（ウェブページのデザイン）---
# Pythonコード内に直接HTMLを記述します (Jinja2テンプレート互換)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Raspberry Pi Servo Control</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; background-color: #f0f0f0; }
    .slider-container { width: 90%; max-width: 600px; margin: 30px auto; padding: 20px; border-radius: 10px; background-color: white; box-shadow: 0 4px 8px rgba(0,0,0,0.1); }
    h1 { color: #CC0066; }
    input[type=range] { width: 100%; height: 25px; cursor: pointer; }
    #angleValue { font-size: 2em; font-weight: bold; color: #0056b3; }
</style>
</head>
<body>
    <h1>サーボモーター Web コントロール</h1>
    
    <div class="slider-container">
        <h2>現在の角度: <span id="angleValue">{{ angle }}</span>°</h2>
        <input type="range" min="-90" max="90" value="{{ angle }}" class="slider" id="servoRange" 
               oninput="updateAngle(this.value)" onchange="sendAngle(this.value)">
    </div>

    <p style="margin-top: 40px; font-size: 0.8em;">アクセスIP: {{ pi_ip }}</p>
    <p style="color: #666; font-size: 0.7em;">※ スライダーを動かした後、指を離すかマウスのボタンを離すとサーボが動きます。</p>

    <script>
        // スライダーを動かしたときに現在の角度をリアルタイム表示
        function updateAngle(newAngle) {
            document.getElementById('angleValue').innerText = newAngle;
        }

        // スライダーを離したときにサーバーに角度を送信
        function sendAngle(newAngle) {
            fetch('/move_servo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'angle=' + newAngle // 角度データをサーバーに送る
            }).then(response => {
                if (!response.ok) {
                    alert('エラーが発生しました。Piの電源や pigpiod の状態を確認してください。');
                }
            });
        }
    </script>
</body>
</html>
"""

# --- Flaskのルーティング ---

@app.route('/')
def index():
    # PiのIPアドレスを取得（表示用）
    try:
        pi_ip = os.popen('hostname -I').read().split()[0]
    except:
        pi_ip = "localhost"
        
    # テンプレートに変数を渡して表示
    # servo.angleは初期値として使われます
    return render_template_string(HTML_TEMPLATE, angle=int(servo.angle), pi_ip=pi_ip)

@app.route('/move_servo', methods=['POST'])
def move_servo():
    # POSTリクエストから角度データを受け取る
    try:
        new_angle = float(request.form.get('angle'))
        
        # サーボの角度を設定
        servo.angle = new_angle
        
        # 成功を返す
        return "OK", 200
    except Exception as e:
        print(f"サーボエラー: {e}", file=sys.stderr)
        return "Internal Server Error", 500

# Piの外部からアクセスできるようにhost='0.0.0.0'で起動
if __name__ == '__main__':
    # 0.0.0.0で起動することで、LAN内の他のデバイスからアクセス可能になります。
    app.run(host='0.0.0.0', port=8000, debug=False)