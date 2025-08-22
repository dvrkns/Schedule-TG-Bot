#!/usr/bin/env python3
"""The entry point for the Telegram bot schedule."""

from src.bot.main import Bot


def main():
    """Main function."""
    bot = Bot()
    bot.run()


if __name__ == "__main__":
    main()
