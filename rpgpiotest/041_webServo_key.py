from flask import Flask, render_template_string, request
from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
import os
import sys

# --- 初期設定 (前回と同じ) ---
try:
    factory = PiGPIOFactory()
    servo = AngularServo(18, min_pulse_width=0.0005, max_pulse_width=0.0024, pin_factory=factory)
except Exception as e:
    print("エラー: 'sudo pigpiod' を実行してデーモンを起動してください。")
    sys.exit(1)

app = Flask(__name__)

# --- HTML/JS (ここがパワーアップ！) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<title>Keyboard Servo Control</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    body { font-family: sans-serif; text-align: center; margin-top: 50px; background: #222; color: white; }
    .container { width: 90%; max-width: 600px; margin: auto; background: #333; padding: 20px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
    input[type=range] { width: 100%; height: 30px; cursor: pointer; accent-color: #ff0055; }
    #val { font-size: 2.5em; color: #ff0055; font-weight: bold; }
    .instructions { margin-top: 20px; padding: 10px; background: #444; border-radius: 5px; font-size: 0.9em; text-align: left; }
    .key { display: inline-block; padding: 3px 8px; background: #666; border-radius: 4px; border-bottom: 2px solid #444; margin: 0 2px; font-family: monospace; }
</style>
</head>
<body>
    <div class="container">
        <h1>Keyboard Control</h1>
        <p>Angle: <span id="val">{{ angle }}</span>&deg;</p>
        
         <input type="range" min="-90" max="90" value="{{ angle }}" id="slider"
             oninput="handleInput(this.value)"
             onchange="send(this.value)">
               
        <!-- 追加: 左右ボタン -->
        <div style="margin-top:16px; display:flex; justify-content:center; gap:12px;">
            <button id="btnLeft" onclick="send(currentAngle - step)" style="padding:10px 18px; font-size:1em;">◀ Left</button>
            <button id="btnRight" onclick="send(currentAngle + step)" style="padding:10px 18px; font-size:1em;">Right ▶</button>
        </div>

        <div class="instructions">
            <p><b>キーボード操作:</b></p>
            <p><span class="key">→</span> or <span class="key">D</span> : 右へ回転 (+5°)</p>
            <p><span class="key">←</span> or <span class="key">A</span> : 左へ回転 (-5°)</p>
            <p><span class="key">Space</span> : 中央 (0°) にリセット</p>
        </div>
        
        <p style="font-size:small; color:gray; margin-top:20px;">IP: {{ ip }}</p>
    </div>

    <script>
        let currentAngle = {{ angle }};
        const step = 25; // 1回押すごとに動く角度

        // 値を表示だけ更新する関数
        function updateDisplay(val) {
            document.getElementById('val').innerText = val;
            currentAngle = parseInt(val);
        }

        // oninput 時にサーボを動かすためのデバウンスハンドラ
        let sendTimer = null;
        const SEND_DELAY = 50; // ms
        function handleInput(val) {
            // 表示は即時更新
            updateDisplay(val);
            // 送信は短い遅延でデバウンス
            if (sendTimer) clearTimeout(sendTimer);
            sendTimer = setTimeout(() => {
                send(val);
                sendTimer = null;
            }, SEND_DELAY);
        }

        // サーバーに送信する関数
        function send(angle) {
            // 範囲チェック (-90 〜 90)
            if (angle > 90) angle = 90;
            if (angle < -90) angle = -90;
            
            // スライダーと表示を同期
            document.getElementById('slider').value = angle;
            document.getElementById('val').innerText = angle;
            currentAngle = parseInt(angle);

            // 送信
            fetch('/move', {
                method: 'POST',
                headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                body: 'angle=' + angle
            }).catch(err => console.error('Error:', err));
        }

        // ★ここがキーボード監視の主役★
        document.addEventListener('keydown', function(event) {
            // 矢印右 or Dキー
            if (event.key === "ArrowRight" || event.key === "d" || event.key === "D") {
                send(currentAngle + step);
            }
            // 矢印左 or Aキー
            else if (event.key === "ArrowLeft" || event.key === "a" || event.key === "A") {
                send(currentAngle - step);
            }
            // スペースキー
            else if (event.key === " ") {
                event.preventDefault(); // 画面スクロール防止
                send(0);
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    try:
        ip = os.popen('hostname -I').read().split()[0]
    except:
        ip = "unknown"
    return render_template_string(HTML_TEMPLATE, angle=int(servo.angle), ip=ip)

@app.route('/move', methods=['POST'])
def move():
    try:
        angle = float(request.form.get('angle'))
        servo.angle = angle
        return "OK"
    except:
        return "Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)