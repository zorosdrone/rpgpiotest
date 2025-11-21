# rpgpiotest

小さな Raspberry Pi 用テストプロジェクト（LED / Servo / Web UI など）。

## 📋 含まれるスクリプト

- `01_ledTest.py` - ACT LED（または GPIO 27）を点滅させるテスト
- `02_sarvo.py` - 基本的なサーボ制御テスト (gpiozero デフォルト)
- `03_servo_pro.py` - pigpio を使った高精度サーボ制御
- `04_webServo.py` - pigpio を使って AngularServo を Web UI で操作

## 🚀 クイックセットアップ

Raspberry Pi OS を再インストール後、以下のいずれかの方法でセットアップしてください。

### 方法 1: Bash スクリプト (推奨)

```bash
git clone https://github.com/zorosdrone/rpgpiotest.git ~/rpgpiotest
cd ~/rpgpiotest
chmod +x setup.sh
./setup.sh
```

### 方法 2: Python スクリプト

```bash
git clone https://github.com/zorosdrone/rpgpiotest.git ~/rpgpiotest
cd ~/rpgpiotest
python3 setup_rpi.py
```

### 方法 3: 手動セットアップ

```bash
# システムパッケージの更新
sudo apt-get update
sudo apt-get upgrade -y

# 必須パッケージのインストール
sudo apt-get install -y python3 python3-pip pigpio python3-pigpio

# Python ライブラリのインストール
pip3 install gpiozero pigpio flask RPi.GPIO

# pigpiod の有効化と起動
sudo systemctl enable pigpiod
sudo systemctl start pigpiod

# GPIO アクセス権の設定
sudo usermod -a -G gpio pi
```

## 📝 使い方

### LED テスト
```bash
python3 01_ledTest.py
```

### サーボ制御テスト
```bash
# 基本的なテスト
python3 02_sarvo.py

# 高精度テスト (pigpio 使用)
python3 03_servo_pro.py
```

### Web UI でサーボ制御

```bash
# pigpiod が起動していることを確認
sudo systemctl status pigpiod

# 仮想環境を有効化
source venv/bin/activate

# サーバー起動
python3 04_webServo.py

# ブラウザでアクセス
# http://<Raspberry_Pi_IP>:8000

# 終了後は仮想環境を無効化
deactivate
```

Raspberry Pi のIPアドレスを確認：
```bash
hostname -I
```

## ⚙️ 必要な環境

- **Raspberry Pi** (Zero W, Zero 2 W, 3, 4, 5 対応)
- **Raspberry Pi OS** (Lite/Full どちらでも可)
- **Python 3.7以上**

## 📦 インストールされるパッケージ

### システムパッケージ
- python3, python3-pip, python3-venv
- git
- pigpio, python3-pigpio

### Python パッケージ
- gpiozero - GPIO制御ライブラリ
- pigpio - 高精度GPIO制御
- flask - Web UI フレームワーク
- RPi.GPIO - GPIO操作用ライブラリ

## 🔧 トラブルシューティング

### pigpiod が起動しない
```bash
sudo systemctl start pigpiod
sudo systemctl status pigpiod
```

### GPIO アクセス権エラー
再起動してから実行してください：
```bash
sudo reboot
```

### Web UI にアクセスできない
1. Raspberry Pi と同じネットワークに接続していることを確認
2. ファイアウォール設定を確認 (ポート8000が開いているか)
3. `hostname -I` で IP アドレスを確認

### インポートエラー
必要なパッケージをインストール：
```bash
pip3 install gpiozero pigpio flask RPi.GPIO
```

## 📌 注意事項

- 実行には Raspberry Pi の GPIO アクセス権が必要です
- pigpiod は自動起動に設定されます
- Web UI は同一ネットワーク内のデバイスからアクセス可能です
- Ctrl+C でプログラムを終了できます

## 📄 ライセンス

このプロジェクトのコードは自由に使用・改変できます。

---

**最終更新**: 2025年11月21日
