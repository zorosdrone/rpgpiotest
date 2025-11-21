#!/usr/bin/env python3

"""
Raspberry Pi プロジェクト更新スクリプト (Python版)
GitHub から最新コードを自動的に取得します

使用方法:
    python3 update.py
"""

import subprocess
import sys
import os

class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}{Colors.ENDC}\n")

def print_step(step_num, total, text):
    print(f"{Colors.BOLD}{Colors.BLUE}[{step_num}/{total}]{Colors.ENDC} {text}...")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.ENDC}\n")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.ENDC}\n")

def print_info(text):
    print(f"{Colors.YELLOW}ℹ {text}{Colors.ENDC}")

def run_command(cmd, description=""):
    """コマンドを実行"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        if description:
            print_success(description)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        if description:
            print_error(f"{description} - {e.stderr}")
        else:
            print_error(f"コマンド実行エラー: {e.stderr}")
        return None

def main():
    print_header("rpgpiotest プロジェクト更新スクリプト")
    
    # プロジェクトディレクトリを取得
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # ステップ 1: 現在の状態を確認
    print_step(1, 3, "現在の状態を確認中")
    print()
    run_command("git status", "")
    print()
    
    # ステップ 2: 最新コードを取得
    print_step(2, 3, "GitHub から最新コードを取得中")
    result = run_command("git pull origin main", "コード更新")
    
    # ステップ 3: 更新内容を表示
    print_step(3, 3, "更新内容を表示中")
    print()
    print(f"{Colors.BOLD}最新 3 つのコミット:{Colors.ENDC}")
    print(run_command("git log --oneline -3", ""))
    print()
    
    # 完了メッセージ
    print_header("更新完了！")
    
    print(f"{Colors.BOLD}📌 次のステップ:{Colors.ENDC}")
    print("  1. 仮想環境を有効化:")
    print("     source venv/bin/activate")
    print("  2. プログラムを実行:")
    print("     python3 04_webServo.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}更新をキャンセルしました{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"予期しないエラーが発生しました: {e}")
        sys.exit(1)
