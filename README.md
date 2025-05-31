# ArcticVPN Telegram Bot

🤖 Telegram бот для предоставления услуг VPN-сервиса ArcticVPN: интеграция с Marzban API, оплата через YooKassa, реферальная система, база SQLite и эксплуатация в Docker.

## ⚠️ Важно

Бот **не разворачивает Marzban автоматически**.  
Перед использованием необходимо вручную развернуть и настроить Marzban по инструкции из [репозитория Marzban](https://github.com/Gozargah/Marzban).  
Бот лишь подключается к уже работающему экземпляру Marzban через его API.


## 📦 Возможности

- Асинхронная работа на базе `aiogram`
- Подключение к Marzban API
- Оплата через YooKassa
- Реферальная система
- Работа с SQLite через `aiosqlite`
- Ручная рассылка сообщений пользователям бота (manual_notifications.py)
- Поддержка Docker и docker-compose

## 🏗️ Стек

- Python 3.11
- [aiogram 3.x](https://docs.aiogram.dev/)
- [aiosqlite](https://github.com/omnilib/aiosqlite)
- [YooKassa SDK](https://github.com/yoomoney/yookassa-sdk-python)
- [Marzban API](https://github.com/Gozargah/Marzban)
- APScheduler (планировщик задач)
- Docker / Docker Compose

## 📁 Структура проекта

```
.
├── .dockerignore
├── docker-compose.yml
├── Dockerfile
├── env/
│   └── .env
├── database/
│   └── subscriptions.sqlite
└── bot/
    ├── run.py
    ├── config.py
    ├── requirements.txt
    ├── manual_notifications.py
    └── app/
        ├── database.py
        ├── handlers.py
        ├── keyboards.py
        ├── utils.py
        └── yoo_kassa.py

```

## 🚀 Запуск через Docker

### Клонирование репозитория

```bash
git clone https://github.com/Korovin-L/ArcticVPN-Telegram-Bot.git
cd ArcticVPN-Telegram-Bot
```

### Конфигурация через `.env`

Заполните `.env` в директории `env/`:

```env
# Telegram
ADMIN_TELEGRAM_ID="admin-id"
BOT_TOKEN="bot-token"

# Marzban
MARZBAN_URL="https://example.com"
MARZBAN_USERNAME="username"
MARZBAN_PASSWORD="password"

# YooKassa
YOOKASSA_ID="id"
YOOKASSA_SECRET_KEY="key"

# Keyboard
TELETYPE_INSTRUCTION = "https://teletype.in/..."
TELEGRAPH_TERMS = "https://telegra.ph/...."
VPN_CONNECT_TEMPLATE = "https://sub.example.com/?url=v2raytun://import/{sub_url}"
```

### Сборка и запуск

```bash
docker compose up -d
```

### Остановка

```bash
docker compose down
```

## 🧑‍💻 Автор

Eldar Korovin

**Telegram**: [@korovinL](https://t.me/korovinL)

## 🔑 Лицензия

Этот проект распространяется под лицензией MIT.  

Подробнее см. файл [LICENSE](./LICENSE)