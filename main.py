import sys
import os
import argparse

# Ensure src is in path
sys.path.append(os.getcwd())

from src.config import Config

def main():
    parser = argparse.ArgumentParser(description="GirlfriendGPT - Your AI Companion")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode instead of Telegram Bot mode")
    parser.add_argument("--test-tools", action="store_true", help="Test tool availability")
    args = parser.parse_args()

    Config.validate()

    if args.test_tools:
        from src.tools import get_tools
        print("Available tools:")
        for t in get_tools():
            print(f"- {t.name}: {t.description}")
        return

    if args.cli:
        from src.cli import main as cli_main
        cli_main()
    else:
        from src.telegram_bot import run_bot
        run_bot()

if __name__ == "__main__":
    main()
