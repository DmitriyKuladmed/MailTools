"""Отправка текста из файла в приватный чат Telegram через бота."""

import argparse
from pathlib import Path

import requests

from mailtools.constants import TELEGRAM_MAX_LENGTH
from mailtools.settings import AppSettings, load_settings


def send_message(token: str, chat_id: str, text: str) -> None:
    """Отправляет сообщение в чат Telegram через HTTP API."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    response = requests.post(url, json={"chat_id": chat_id, "text": text})
    if response.status_code != 200 or not response.json().get("ok"):
        raise RuntimeError(f"Telegram error: {response.text}")


def read_text(file_path: Path) -> str:
    """Читает текст из файла и обрезает до лимита Telegram."""
    text = file_path.read_text(encoding="utf-8")
    if len(text) > TELEGRAM_MAX_LENGTH:
        text = text[:TELEGRAM_MAX_LENGTH]
    return text


def parse_args(settings: AppSettings, argv: list[str] | None = None) -> argparse.Namespace:
    """Парсит аргументы CLI, подставляя значения по умолчанию из настроек"""
    parser = argparse.ArgumentParser(description="Отправить содержимое .txt в Telegram чат.")
    parser.add_argument("file", type=Path, help="Путь к .txt файлу с сообщением.")
    parser.add_argument(
        "--token",
        default=settings.bot_token,
        help="Токен бота Telegram (или переменная TELEGRAM_BOT_TOKEN).",
    )
    parser.add_argument(
        "--chat-id",
        dest="chat_id",
        default=settings.chat_id,
        help="chat_id чата (или переменная TELEGRAM_CHAT_ID).",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    """CLI вход: отправка текста из файла в выбранный чат"""
    settings = load_settings()
    args = parse_args(settings, argv)
    if not args.token or not args.chat_id:
        print("Нужны token и chat_id (флаги или переменные окружения).")
        return 1
    if not args.file.exists():
        print(f"File not found: {args.file}")
        return 1

    text = read_text(args.file)
    try:
        send_message(args.token, args.chat_id, text)
    except Exception as exc:
        print(f"Failed to send message: {exc}")
        return 1

    print("Message sent successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

