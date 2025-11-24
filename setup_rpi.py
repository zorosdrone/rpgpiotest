#!/usr/bin/env python3

"""
Raspberry Pi OS セットアップ スクリプト (Python版)
rpgiotestプロジェクト用

使用方法:
    python3 setup_rpi.py              # 通常実行（高速、アップデートなし）
    python3 setup_rpi.py --update      # アップデートを実行
    python3 setup_rpi.py -u            # アップデートを実行 (短縮形)

このスクリプトは以下の処理を自動化します:
    - システムパッケージの更新 (--update で実行可能、デフォルトはスキップ)
    - 必須Pythonライブラリのインストール
    - pigpiod の自動起動設定
    - GPIO アクセス権の設定
"""

import subprocess
import sys
import os
import platform

# カラー出力用
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

def run_command(cmd, description="", sudo=False):
    """コマンドを実行"""
    try:
        if sudo:
            cmd = f"sudo {cmd}"
        
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

def is_raspberry_pi():
    """Raspberry Pi かどうかを確認"""
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model = f.read().strip()
            return 'Raspberry Pi' in model
    except:
        return False

def main():
    print_header("Raspberry Pi GPIO テストプロジェクト セットアップ")
    
    # コマンドラインオプションの確認
    # Raspberry Pi Zero 2 W では時間がかかるため、デフォルトでスキップ
    skip_update = not ("--update" in sys.argv or "-u" in sys.argv)
    if skip_update:
        print_info("システムアップデートをスキップします（高速化のため）")
        print_info("アップデートする場合は '--update' オプションを使用してください")
        print()
    
    # Raspberry Pi チェック
    if not is_raspberry_pi():
        print_info("このスクリプトは Raspberry Pi 上で実行してください")
        if input("続行しますか? (y/n): ").lower() != 'y':
            print("セットアップをキャンセルしました")
            sys.exit(0)
    
    steps = 7
    
    # ステップ 1: システム更新
    print_step(1, steps, "システムパッケージを更新中")
    if skip_update:
        print_info("システムアップデートをスキップしました（高速化のため）")
        print()
    else:
        print_info("これには5〜10分かかる場合があります")
        run_command("apt-get update", "apt update", sudo=True)
        run_command("apt-get upgrade -y", "apt upgrade", sudo=True)
    
    # ステップ 2: 必須パッケージのインストール
    print_step(2, steps, "必須パッケージをインストール中")
    packages = [
        "python3",
        "python3-pip",
        "python3-venv",
        "git",
        "pigpio",
        "python3-pigpio",
    ]
    run_command(f"apt-get install -y {' '.join(packages)}", 
                "必須パッケージをインストール", sudo=True)
    
    # ステップ 3: Python ライブラリのインストール（仮想環境使用）
    print_step(3, steps, "Python ライブラリをインストール中")
    
    # 仮想環境を作成
    venv_path = os.path.expanduser("~/rpgpiotest/venv")
    if not os.path.exists(venv_path):
        print_info("仮想環境を作成中...")
        run_command("python3 -m venv ~/rpgpiotest/venv", 
                   "仮想環境を作成", sudo=False)
    
    # 仮想環境内の pip を使用してパッケージをインストール
    pip_cmd = os.path.expanduser("~/rpgpiotest/venv/bin/pip")
    
    run_command(f"{pip_cmd} install --upgrade pip", 
               "pip をアップグレード", sudo=False)
    
    python_packages = [
        "gpiozero",
        "pigpio",
        "flask",
        "RPi.GPIO",
    ]
    run_command(f"{pip_cmd} install {' '.join(python_packages)}", 
                "Python ライブラリをインストール", sudo=False)
    
    # ステップ 4: pigpiod の自動起動設定
    print_step(4, steps, "pigpiod サービスを設定中")
    run_command("systemctl enable pigpiod", "pigpiod 自動起動有効化", sudo=True)
    run_command("systemctl start pigpiod", "pigpiod を起動", sudo=True)
    
    # ステップ 5: GPIO グループへの追加
    print_step(5, steps, "GPIO アクセス権を設定中")
    current_user = os.getenv('USER', 'pi')
    run_command(f"usermod -a -G gpio {current_user}", 
                f"ユーザー '{current_user}' を gpio グループに追加", sudo=True)
    print_info("この変更は再起動後に有効になります")
    
    # ステップ 6: プロジェクトディレクトリの確認
    print_step(6, steps, "プロジェクトディレクトリを確認中")
    project_dir = os.path.expanduser("~/rpgpiotest")
    if not os.path.exists(project_dir):
        run_command("git clone https://github.com/zorosdrone/rpgpiotest.git ~/rpgpiotest",
                   "プロジェクトをクローン", sudo=False)
    else:
        os.chdir(project_dir)
        run_command("git pull origin main", "プロジェクトを更新", sudo=False)
    print_success("プロジェクトディレクトリの確認完了")
    
    # ステップ 7: 実行権限の設定
    print_step(7, steps, "実行スクリプトの権限を設定中")
    os.chdir(project_dir)
    subprocess.run("chmod +x *.py setup.sh", shell=True)
    print_success("実行権限を設定しました")
    
    # 完了メッセージ
    print_header("セットアップ完了！")
    
    print(f"{Colors.BOLD}📦 インストール場所:{Colors.ENDC}")
    print("  • Python パッケージ: ~/rpgpiotest/venv 内")
    print()
    
    print(f"{Colors.BOLD}実行可能なプログラム:{Colors.ENDC}")
    print("  • LED テスト:        python3 01_ledTest.py")
    print("  • サーボ テスト:      python3 02_sarvo.py")
    print("  • サーボ Pro:        python3 03_servo_pro.py")
    print("  • Web サーボ制御:    source venv/bin/activate && python3 04_webServo.py")
    print()
    
    print(f"{Colors.BOLD}注意事項:{Colors.ENDC}")
    print("  • pigpiod は自動起動しています")
    print("  • Python パッケージは仮想環境（venv）内にインストールされています")
    print("  • Web UI を実行する場合は、まず 'source venv/bin/activate' を実行してください")
    print("  • GPIO グループの設定は再起動後に有効になります")
    print("  • Ctrl+C でプログラムを終了できます")
    print()
    
    if is_raspberry_pi():
        reboot = input(f"{Colors.YELLOW}再起動しますか? (y/n): {Colors.ENDC}")
        if reboot.lower() == 'y':
            print("再起動します...")
            subprocess.run("sudo reboot", shell=True)
    
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}セットアップをキャンセルしました{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"予期しないエラーが発生しました: {e}")
        sys.exit(1)
