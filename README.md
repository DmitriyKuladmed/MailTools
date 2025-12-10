# MailTools

Структура:

- `mailtools/` — логика (проверка MX, отправка в Telegram, настройки, константы).
- `scripts/` — точки входа `email_domain_check.py`, `telegram_sender.py`.
- `tests/` — юнит-тесты.
- `ARCHITECTURE.md` — описание архитектуры аутрича на ~1200 адресов.

## Требования

- Python 3.11
- Зависимости: `pip install -r requirements.txt`

## Проверка MX доменов

1. Подготовьте файл `emails.txt`, по одному email в строке.
2. Запуск:
   ```
   python scripts/email_domain_check.py emails.txt
   ```
3. Вывод: `<email>\t<статус>`, где статус один из:
   - `домен валиден`
   - `домен отсутствует`
   - `MX-записи отсутствуют или некорректны`

## Отправка текста в Telegram

1. Получите токен бота: напишите `@BotFather` → `/newbot` → получите `TELEGRAM_BOT_TOKEN`.
2. Узнайте `chat_id` приватного чата (например, через `@RawDataBot` или временно добавив бота и посмотрев `chat.id` в обновлениях).
3. Подготовьте текст в `message.txt` (до 4096 символов).
4. Запуск (через флаги или переменные окружения):
   ```
   python scripts/telegram_sender.py message.txt --token YOUR_TOKEN --chat-id YOUR_CHAT_ID
   ```
   или
   ```
   set TELEGRAM_BOT_TOKEN=YOUR_TOKEN
   set TELEGRAM_CHAT_ID=YOUR_CHAT_ID
    python scripts/telegram_sender.py message.txt
   ```

## Настройки окружения

- Переменные читаются через Pydantic Settings из `.env` (или окружения):
  ```
  TELEGRAM_BOT_TOKEN=...
  TELEGRAM_CHAT_ID=...
  ```

## Тесты

- Запуск: `pytest`
- Локальный прогон: 6 тестов пройдено (`pytest`, Python 3.11).

## Архитектура

См. `ARCHITECTURE.md` для описания инфраструктуры, ротации, мониторинга и оценки стоимости.