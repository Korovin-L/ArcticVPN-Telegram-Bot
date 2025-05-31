import os
from dotenv import load_dotenv

# Загружаем .env из поддиректории ./env/
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), 'env', '.env'))

ADMIN_TELEGRAM_ID = os.getenv("ADMIN_TELEGRAM_ID")
BOT_TOKEN = os.getenv('BOT_TOKEN')
MARZBAN_URL = os.getenv('MARZBAN_URL')
MARZBAN_USERNAME = os.getenv('MARZBAN_USERNAME')
MARZBAN_PASSWORD = os.getenv('MARZBAN_PASSWORD')

YOOKASSA_ID = os.getenv("YOOKASSA_ID")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY")

TELETYPE_INSTRUCTION = os.getenv("TELETYPE_INSTRUCTION")
TELEGRAPH_TERMS = os.getenv("TELEGRAPH_TERMS")
VPN_CONNECT_TEMPLATE = os.getenv("VPN_CONNECT_TEMPLATE")

prices = {1: 99, # мес.: цена
          3: 299,
          6: 599}

# Основные тексты
main_text = (
    '❄️ ArcticVPN - Сервис для бесперебойного доступа в Интернет.\n\n'
    '⚠️ <b>Перед использованием обязательно прочтите условия использования и инструкцию!</b>'
)
connect_text = lambda device, market: (
    f'<b>🌐 Подключение к ArcticVPN на {device}</b>\n\n'
    f'1️⃣ Скачайте приложение с {market}\n'
    '2️⃣ Нажмите на кнопку «Подключиться»'
)
