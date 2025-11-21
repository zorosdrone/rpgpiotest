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

# オプション: --force (-f) : 作業ツリーを強制的に origin/main に合わせる (reset --hard)
#           --stash (-s) : 未コミット変更を stash して pull 後に pop する

FORCE=false
STASH=false
while [ "$#" -gt 0 ]; do
	case "$1" in
		-f|--force)
			FORCE=true; shift ;; 
		-s|--stash)
			STASH=true; shift ;;
		-h|--help)
			echo "Usage: $0 [--force|-f] [--stash|-s]"; exit 0 ;;
		*) echo "Unknown option: $1"; echo "Usage: $0 [--force|-f] [--stash|-s]"; exit 1 ;;
	esac
done

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

# 作業ツリーがクリーンか確認
if [ -n "$(git status --porcelain)" ]; then
	echo "*** 注意: 作業ツリーに未コミットの変更があります。" >&2
	echo "現在の設定では、VS Code の SFTP が保存時にリモート上のファイルを上書きしている可能性があります。" >&2
	echo "以下のいずれかを実行してください: 1) 変更をコミットして push する, 2) --stash を使う, 3) --force を使ってリセットして上書きする" >&2
	if [ "$FORCE" = true ]; then
		echo "--force を指定したため、origin/main に強制リセットします..."
		git fetch origin
		git reset --hard origin/main
	elif [ "$STASH" = true ]; then
		echo "--stash を指定したため、変更を stash して pull します..."
		git stash push -m "auto-stash before update.sh"
		git pull origin main
		echo "stash を pop します（衝突がある場合は手動で解決してください）"
		git stash pop || echo "stash pop に失敗しました。手動で解決してください。"
	else
		echo "処理を中止します。必要なら --force または --stash を指定してください。"
		exit 1
	fi
else
	echo "作業ツリーはクリーンです。pull を実行します。"
	git pull origin main
fi
echo ""

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
