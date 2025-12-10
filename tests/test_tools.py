from pathlib import Path

import dns.exception
import dns.resolver
import pytest

from mailtools import email_checker as edc
from mailtools import telegram_sender as ts
from mailtools.settings import load_settings


class FakeResponse:
    def __init__(self, status_code=200, ok=True, text="ok"):
        self.status_code = status_code
        self._ok = ok
        self._text = text

    def json(self):
        return {"ok": self._ok}

    @property
    def text(self):
        return self._text


class FakeResolver:
    def resolve(self, domain, record_type):
        assert record_type == "MX"
        if domain == "valid.com":
            return ["mx.valid.com"]
        if domain == "nomx.com":
            raise dns.resolver.NoAnswer
        raise dns.resolver.NXDOMAIN


def test_validate_emails(monkeypatch, tmp_path):
    # Prepare input file
    data = "user@valid.com\nbroken-email\nuser@nomx.com\nuser@missing.com\n"
    source = tmp_path / "emails.txt"
    source.write_text(data, encoding="utf-8")

    # Patch resolver
    monkeypatch.setattr(dns.resolver, "Resolver", lambda: FakeResolver())

    results = list(edc.validate_emails(edc.iter_emails(source)))

    assert results == [
        ("user@valid.com", edc.STATUS_VALID),
        ("broken-email", edc.STATUS_NO_DOMAIN),
        ("user@nomx.com", edc.STATUS_BAD_MX),
        ("user@missing.com", edc.STATUS_NO_DOMAIN),
    ]


def test_read_text_truncates(monkeypatch, tmp_path):
    long_text = "a" * 5000
    file_path = tmp_path / "msg.txt"
    file_path.write_text(long_text, encoding="utf-8")
    result = ts.read_text(file_path)
    assert len(result) == 4096


def test_send_message_success(monkeypatch):
    posted = {}

    def fake_post(url, json):
        posted["url"] = url
        posted["json"] = json
        return FakeResponse()

    monkeypatch.setattr(ts.requests, "post", fake_post)
    ts.send_message("TOKEN", "123", "hello")
    assert posted["url"].endswith("/botTOKEN/sendMessage")
    assert posted["json"] == {"chat_id": "123", "text": "hello"}


def test_send_message_failure(monkeypatch):
    def fake_post(url, json):
        return FakeResponse(status_code=400, ok=False, text="bad")

    monkeypatch.setattr(ts.requests, "post", fake_post)
    with pytest.raises(RuntimeError):
        ts.send_message("TOKEN", "123", "hello")


def test_settings_from_env(monkeypatch):
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "ENV_TOKEN")
    monkeypatch.setenv("TELEGRAM_CHAT_ID", "ENV_CHAT")
    settings = load_settings()
    args = ts.parse_args(settings, ["message.txt"])
    # parse_args defaults from settings when no CLI args provided
    assert args.token == "ENV_TOKEN"
    assert args.chat_id == "ENV_CHAT"


def test_settings_dotenv(tmp_path, monkeypatch):
    dotenv = tmp_path / ".env"
    dotenv.write_text("TELEGRAM_BOT_TOKEN=FILE_TOKEN\nTELEGRAM_CHAT_ID=FILE_CHAT\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    settings = load_settings()
    assert settings.bot_token == "FILE_TOKEN"
    assert settings.chat_id == "FILE_CHAT"

