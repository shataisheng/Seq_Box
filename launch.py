#!/usr/bin/env python3
"""
Seq_Box 快速启动入口
用法:
    python launch.py          → 启动 GUI
    python launch.py --cli    → 进入 CLI 模式
    python launch.py --help   → 查看帮助
"""

import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))


def check_deps():
    """检查并提示安装缺失依赖"""
    missing = []
    try:
        import PyQt6
    except ImportError:
        missing.append("PyQt6")
    try:
        import qtawesome
    except ImportError:
        missing.append("qtawesome")

    if missing:
        print(f"[提示] 缺少依赖: {', '.join(missing)}")
        ans = input("是否现在自动安装？[Y/n] ").strip().lower()
        if ans in ("", "y", "yes"):
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install"] + missing + ["-q"]
            )
            print("[完成] 依赖安装成功\n")
        else:
            print("[中止] 请手动运行: pip install PyQt6 qtawesome")
            sys.exit(1)


def launch_gui():
    check_deps()
    from seqbox.gui.main_window import main
    main()


def launch_cli(args):
    from seqbox.cli import main as cli_main
    sys.argv = ["seqbox"] + args
    cli_main()


def print_help():
    print("""
╔══════════════════════════════════════╗
║         Seq_Box  v0.4.0             ║
║  DNA / 蛋白质序列操作工具箱          ║
╚══════════════════════════════════════╝

用法:
  python launch.py              启动 GUI 界面
  python launch.py --cli [CMD]  使用命令行模式
  python launch.py --help       显示此帮助

CLI 示例:
  python launch.py --cli fasta clean input.fasta -o output.fasta
  python launch.py --cli fasta split input.fasta -n 100
  python launch.py --cli --help   查看所有 CLI 命令
""")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "--gui":
        launch_gui()
    elif args[0] == "--cli":
        launch_cli(args[1:])
    elif args[0] in ("--help", "-h"):
        print_help()
    else:
        # 不认识的参数，直接转给 CLI
        launch_cli(args)
