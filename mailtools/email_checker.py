import sys
import dns.resolver
import dns.exception

from pathlib import Path
from typing import Iterable, Tuple

from mailtools.constants import STATUS_BAD_MX, STATUS_NO_DOMAIN, STATUS_VALID


def iter_emails(source: Path) -> Iterable[str]:
    """Читает файл и возвращает email-адреса (игнорируя пустые строки и комментарии)."""
    with source.open(encoding="utf-8") as f:
        for line in f:
            email = line.strip()
            if email and not email.startswith("#"):
                yield email


def extract_domain(email: str) -> str | None:
    """Извлекает доменную часть из email или возвращает None при неверном формате."""
    parts = email.rsplit("@", 1)
    if len(parts) != 2 or not parts[1]:
        return None
    return parts[1].lower()


def check_domain(domain: str, resolver: dns.resolver.Resolver) -> str:
    """Проверяет наличие MX-записей домена и возвращает текстовый статус."""
    try:
        answers = resolver.resolve(domain, "MX")
        if not answers:
            return STATUS_BAD_MX
        return STATUS_VALID
    except dns.resolver.NXDOMAIN:
        return STATUS_NO_DOMAIN
    except (dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.exception.Timeout):
        return STATUS_BAD_MX
    except Exception:
        return STATUS_BAD_MX


def validate_emails(emails: Iterable[str]) -> Iterable[Tuple[str, str]]:
    """Проверяет список email и отдаёт пары (email, статус)."""
    resolver = dns.resolver.Resolver()
    for email in emails:
        domain = extract_domain(email)
        if not domain:
            yield email, STATUS_NO_DOMAIN
            continue
        status = check_domain(domain, resolver)
        yield email, status


def main() -> int:
    """CLI вход: принимает путь к файлу с email и печатает статусы."""
    if len(sys.argv) < 2:
        print("Использование: python -m scripts.email_domain_check emails.txt")
        return 1

    source = Path(sys.argv[1])
    if not source.exists():
        print(f"Файл не найден: {source}")
        return 1

    for email, status in validate_emails(iter_emails(source)):
        print(f"{email}\t{status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

