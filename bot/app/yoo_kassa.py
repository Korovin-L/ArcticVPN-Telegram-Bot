import uuid
import logging
from typing import Tuple, Optional
from yookassa import Configuration, Payment

import config

# Логгер
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Настройки YooKassa
Configuration.account_id = config.YOOKASSA_ID
Configuration.secret_key = config.YOOKASSA_SECRET_KEY


async def create_payment(price: float, user_id: int, period: int) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Создает платёж и возвращает:
    (confirmation_url, idempotence_key, payment_id, status)
    """
    try:
        idempotence_key = str(uuid.uuid4())
        payment = Payment.create({
            "amount": {
                "value": f"{price:.2f}",
                "currency": "RUB"
            },
            "payment_method_data": {
                "type": "sbp"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": "https://t.me/username_bot"  # Замените на ваш URL
            },
            "capture": True,
            "metadata": {
                "user_id": str(user_id)
            },
            "description": f"Оплата подписки на {period} мес."
        }, idempotence_key)

        return payment.confirmation.confirmation_url, idempotence_key, payment.id, payment.status

    except Exception as e:
        logger.error(f"❌ Ошибка при создании платежа: {e}")
        return None, None, None, None


async def check_payment(payment_id: str) -> bool:
    """
    Проверяет, был ли платёж оплачен.
    """
    try:
        payment = Payment.find_one(payment_id)
        return payment.paid
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке платежа: {e}")
        return False