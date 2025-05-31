async def send_message_to_user(user_id: int):
    from run import bot
    await bot.send_message(user_id, "🎁 Вы получили бонусные 7 дней подписки за друга!")
