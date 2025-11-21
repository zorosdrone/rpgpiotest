#!/bin/bash

###############################################################################
# Raspberry Pi OS セットアップスクリプト
# rpgpiotestプロジェクト用
# 
# 使用方法:
#   chmod +x setup.sh
#   ./setup.sh
###############################################################################

set -e  # エラーで終了

echo "================================================"
echo "  Raspberry Pi GPIO テストプロジェクト セットアップ"
echo "================================================"
echo ""

# 1. システム更新
echo "[1/7] システムパッケージを更新中..."
sudo apt-get update
sudo apt-get upgrade -y
echo "✓ システム更新完了"
echo ""

# 2. 必須パッケージのインストール
echo "[2/7] 必須パッケージをインストール中..."
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    pigpio \
    python3-pigpio
echo "✓ 必須パッケージをインストール完了"
echo ""

# 3. Pythonライブラリのインストール（グローバル）
echo "[3/7] Python ライブラリをインストール中..."
pip3 install --upgrade pip
pip3 install \
    gpiozero \
    pigpio \
    flask \
    RPi.GPIO
echo "✓ Python ライブラリをインストール完了"
echo ""

# 4. pigpiod サービスの自動起動設定
echo "[4/7] pigpiod サービスを設定中..."
sudo systemctl enable pigpiod
sudo systemctl start pigpiod
echo "✓ pigpiod を自動起動に設定しました"
echo ""

# 5. プロジェクトディレクトリの確認
echo "[5/7] プロジェクトディレクトリを確認中..."
if [ ! -d "$HOME/rpgpiotest" ]; then
    echo "  プロジェクトディレクトリをクローンしています..."
    cd $HOME
    git clone https://github.com/zorosdrone/rpgpiotest.git
    cd rpgpiotest
else
    echo "  既にプロジェクトディレクトリが存在します"
    cd $HOME/rpgpiotest
    git pull origin main
fi
echo "✓ プロジェクトディレクトリの確認完了"
echo ""

# 6. GPIO ユーザーグループの設定
echo "[6/7] GPIO アクセス権を設定中..."
sudo usermod -a -G gpio pi
echo "✓ GPIO アクセス権を設定しました（再起動が必要な場合があります）"
echo ""

# 7. 実行権限の設定
echo "[7/7] 実行スクリプトの権限を設定中..."
chmod +x *.py
echo "✓ 実行権限を設定しました"
echo ""

echo "================================================"
echo "  セットアップ完了！"
echo "================================================"
echo ""
echo "実行可能なプログラム:"
echo "  • LED テスト:        python3 01_ledTest.py"
echo "  • サーボ テスト:      python3 02_sarvo.py"
echo "  • サーボ Pro:        python3 03_servo_pro.py"
echo "  • Web サーボ制御:    python3 04_webServo.py"
echo ""
echo "注意事項:"
echo "  • pigpiod は自動起動しています"
echo "  • Web UI の場合、ブラウザから http://<Pi_IP>:8000 にアクセス"
echo "  • Ctrl+C でプログラムを終了できます"
echo ""
echo "トラブル時は README.md を参照してください"
echo ""
