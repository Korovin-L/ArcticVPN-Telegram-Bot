import asyncio
from datetime import datetime
from typing import List
from run import bot
from marzban import MarzbanAPI
from app.database import get_all_users
from config import MARZBAN_URL, MARZBAN_USERNAME, MARZBAN_PASSWORD, ADMIN_TELEGRAM_ID
from aiogram.enums import ParseMode

api = MarzbanAPI(base_url=MARZBAN_URL)


async def get_inactive_users() -> List[str]:
    """Получает список пользователей, которые не использовали трафик и у которых активная подписка."""
    inactive_users = []
    users = await get_all_users()
    token = await api.get_token(username=MARZBAN_USERNAME, password=MARZBAN_PASSWORD)
    current_timestamp = int(datetime.now().timestamp())

    for user_id in users:
        user = await api.get_user(username=user_id, token=token.access_token)
        if user.used_traffic == 0 and user.expire > current_timestamp:
            inactive_users.append(user.username)

    return inactive_users


async def safe_send_message(user_id: str, message: str):
    """Отправляет сообщение пользователю и обрабатывает возможные ошибки."""
    try:
        await bot.send_message(
            chat_id=user_id,
            text=message,
            parse_mode=ParseMode.HTML
        )
        print(f"✅ Отправлено: {user_id}")
    except Exception as e:
        print(f"❌ Ошибка при отправке уведомления {user_id}: {e}")


async def send_messages_to_users(user_ids: List[str], message: str):
    """Отправляет сообщение списку пользователей."""
    for user_id in user_ids:
        await safe_send_message(user_id, message)


async def send_message_to_inactive_users(message: str):
    """Отправляет сообщение пользователям, которые не использовали трафик и у которых активная подписка."""
    users = await get_inactive_users()
    users.append(ADMIN_TELEGRAM_ID)
    await send_messages_to_users(users, message)


async def send_message_to_all_users(message: str):
    """Отправляет сообщение всем пользователям."""
    users = await get_all_users()
    users.append(ADMIN_TELEGRAM_ID)
    await send_messages_to_users(users, message)


async def main():
    """
    Ручная рассылка уведомлений пользователям.
    """
    message_all = (
        '<b>🎉 Отличные новости!</b>\n\n'
        '📉 Мы <b>снизили цены</b> на подписку!\n'
        'Теперь пользоваться нашим сервисом стало ещё выгоднее.\n\n'
        '👉 Нажмите /start, чтобы выбрать новый тариф.'
    )

    message_inactive = (
        '<b>⚠️ Возникли трудности с подключением?</b>\n\n'
        'Обратитесь в поддержку, и мы поможем!\n'
        '👷 @id'
    )

    # Выбрать нужное:
    # await send_message_to_all_users(message_all)
    # await send_message_to_inactive_users(message_inactive)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
