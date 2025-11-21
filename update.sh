#!/bin/bash

###############################################################################
# Raspberry Pi プロジェクト更新スクリプト
# GitHub から最新コードを取得します
# 
# 使用方法:
#   chmod +x update.sh
#   ./update.sh
###############################################################################

set -e

echo "================================================"
echo "  rpgpiotest プロジェクト更新スクリプト"
echo "================================================"
echo ""

# プロジェクトディレクトリに移動
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$PROJECT_DIR"

echo "[1/3] 現在の状態を確認中..."
echo ""
git status
echo ""

echo "[2/3] GitHub から最新コードを取得中..."
git pull origin main
echo "✓ コード更新完了"
echo ""

echo "[3/3] 更新内容を表示中..."
echo ""
echo "最新 3 つのコミット:"
git log --oneline -3
echo ""

echo "================================================"
echo "  更新完了！"
echo "================================================"
echo ""
echo "📌 仮想環境を有効化してプログラムを実行："
echo "  source venv/bin/activate"
echo "  python3 04_webServo.py"
echo ""
