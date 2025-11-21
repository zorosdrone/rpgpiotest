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

# システムアップデートをスキップするかどうか
SKIP_UPDATE=false
if [ "$1" = "--skip-update" ] || [ "$1" = "-s" ]; then
    SKIP_UPDATE=true
    echo "⚠ システムアップデートをスキップします"
    echo ""
fi

# 1. システム更新
if [ "$SKIP_UPDATE" = false ]; then
    echo "[1/7] システムパッケージを更新中..."
    echo "⚠ これには5〜10分かかる場合があります..."
    echo "スキップする場合は Ctrl+C を押すか、'./setup.sh --skip-update' で実行してください"
    echo ""
    sudo apt-get update
    sudo apt-get upgrade -y
    echo "✓ システム更新完了"
    echo ""
else
    echo "[1/7] システムアップデートをスキップしました"
    echo ""
fi

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

# 3. Pythonライブラリのインストール（仮想環境使用）
echo "[3/7] Python ライブラリをインストール中..."

# 仮想環境を作成（存在しなければ）
if [ ! -d "venv" ]; then
    echo "  仮想環境を作成中..."
    python3 -m venv venv
fi

# 仮想環境を有効化
source venv/bin/activate

# pip をアップグレード
pip install --upgrade pip

# 必要なパッケージをインストール
pip install \
    gpiozero \
    pigpio \
    flask \
    RPi.GPIO

# 仮想環境を無効化
deactivate

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
echo "📌 使用方法:"
echo "  • 通常実行:           ./setup.sh"
echo "  • アップデートなし:   ./setup.sh --skip-update"
echo ""
echo "📦 インストール場所:"
echo "  • Python パッケージ: ~/rpgpiotest/venv 内"
echo ""
echo "実行可能なプログラム:"
echo "  • LED テスト:        python3 01_ledTest.py"
echo "  • サーボ テスト:      python3 02_sarvo.py"
echo "  • サーボ Pro:        python3 03_servo_pro.py"
echo "  • Web サーボ制御:    source venv/bin/activate && python3 04_webServo.py"
echo ""
echo "注意事項:"
echo "  • pigpiod は自動起動しています"
echo "  • Python パッケージは仮想環境（venv）内にインストールされています"
echo "  • Web UI を実行する場合は、まず 'source venv/bin/activate' を実行してください"
echo "  • GPIO グループの設定は再起動後に有効になります"
echo "  • Ctrl+C でプログラムを終了できます"
echo ""
echo "トラブル時は README.md を参照してください"
echo ""
