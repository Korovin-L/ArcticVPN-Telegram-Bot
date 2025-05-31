import asyncio
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot, Dispatcher

from marzban import MarzbanAPI
from app.database import init_db
from app.handlers import router
from config import BOT_TOKEN, MARZBAN_URL, MARZBAN_PASSWORD, MARZBAN_USERNAME


# Инициализация API и бота
api = MarzbanAPI(base_url=MARZBAN_URL)
bot = Bot(BOT_TOKEN)
dp = Dispatcher()


async def send_expiry_notifications():
    """
    Проверяет, у кого подписка истекает завтра,
    и отправляет предупреждающее сообщение.
    """
    token = await api.get_token(username=MARZBAN_USERNAME, password=MARZBAN_PASSWORD)
    users_response = await api.get_users(token=token.access_token)
    users = users_response.users

    tomorrow = (datetime.now() + timedelta(days=1)).date()

    for user in users:
        expire_timestamp = user.expire
        if not expire_timestamp:
            continue

        expire_date = datetime.fromtimestamp(expire_timestamp).date()
        if expire_date == tomorrow:
            try:
                await bot.send_message(
                    chat_id=user.username,
                    text="⚠️ <b>Ваша подписка истекает завтра!</b>\n\n"
                         "Продлите её заранее, чтобы избежать отключения."
                )
                logging.info(f"Уведомление отправлено: {user.username}")
            except Exception as e:
                logging.warning(f"Ошибка при отправке {user.username}: {e}")


async def start_scheduler():
    """
    Запускает планировщик задач:
    - уведомления об истечении подписки в 12:00 каждый день
    """
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_expiry_notifications, "cron", hour=12, minute=0)
    scheduler.start()
    logging.info("Планировщик запущен")


async def main():
    """
    Точка входа:
    - инициализация базы
    - запуск планировщика
    - запуск Telegram-бота
    """
    await init_db()
    dp.include_router(router)
    await start_scheduler()
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Остановка приложения пользователем")
