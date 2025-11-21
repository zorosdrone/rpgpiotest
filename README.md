# rpgpiotest

小さな Raspberry Pi 用テストプロジェクト（LED / Servo / Web UI など）。

## 📋 含まれるスクリプト

- `01_ledTest.py` - ACT LED（または GPIO 27）を点滅させるテスト
- `02_sarvo.py` - 基本的なサーボ制御テスト (gpiozero デフォルト)
- `03_servo_pro.py` - pigpio を使った高精度サーボ制御
- `04_webServo.py` - pigpio を使って AngularServo を Web UI で操作
- `041_webServo_key.py` - キーボード操作と左右ボタンでサーボを操作する Web UI

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

## 🔄 GitHub から最新コードを取得

セットアップ後、GitHub に更新があった場合は以下のコマンドで最新コードを取得できます。

```bash
cd ~/rpgpiotest

# 方法 1: 直接 git コマンド
git pull origin main

# 方法 2: 自動更新スクリプト (推奨)
./update.sh          # Bash版
# または
python3 update.py    # Python版
```

更新スクリプトは以下を自動で実行します：
- Git の状態確認
- GitHub から最新コードを取得
- 最新のコミット情報を表示

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

# サーバー起動 (基本)
python3 04_webServo.py

# またはキーボード/ボタン操作付きの Web UI
# (スライダーを動かしたときに即座にサーボへ送信されます)
python3 rpgpiotest/041_webServo_key.py

# ブラウザでアクセス
# http://<Raspberry_Pi_IP>:8000

# 終了後は仮想環境を無効化
deactivate
```

Raspberry Pi のIPアドレスを確認：
```bash
hostname -I
```

### Keyboard / Button Web UI (041)

`041_webServo_key.py` はブラウザ上でスライダー、左右ボタン、またはキーボード（←→ / A D / Space）でサーボを操作する Web UI です。

- スライダーは「移動させたとき」にデバウンス送信してサーボを即時更新します（離したときではありません）。
- 左右ボタンで角度をステップ（デフォルト 5°）ずつ増減できます。
- キーボード操作: 矢印キーまたは `A`/`D`、スペースで中央リセット。

実行:
```bash
# 仮想環境を有効化
source venv/bin/activate

# サーバー起動
python3 rpgpiotest/041_webServo_key.py
```

ブラウザで `http://<Raspberry_Pi_IP>:8000` にアクセスして操作します。


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
