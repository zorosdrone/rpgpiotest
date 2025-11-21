# zero_goiptest

小さな Raspberry Pi 用テストプロジェクト（LED / Servo / Web UI など）。

含まれる主なスクリプト:
- `01_ledTest.py` - ACT LED（または GPIO 27）を点滅させるテスト
- `04_webServo.py` - pigpio を使って AngularServo を Web UI で操作するサンプル

使い方:
1. 必要パッケージをインストール:
```
pip install gpiozero pigpio flask
```
2. pigpiod を起動:
```
sudo pigpiod
```
3. サーバー起動:
```
source venv_flask/bin/activate
python3 04_webServo.py
```

注意: 実行には Raspberry Pi の GPIO アクセス権と pigpio デーモンが必要です。
