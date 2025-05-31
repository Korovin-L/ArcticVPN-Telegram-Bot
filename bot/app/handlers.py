import httpx
from datetime import datetime
from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.utils.deep_linking import create_start_link, decode_payload

from marzban import MarzbanAPI, UserCreate, UserModify, ProxySettings
from config import MARZBAN_URL, MARZBAN_USERNAME, MARZBAN_PASSWORD, prices, main_text, connect_text

from app.utils import send_message_to_user
from app.database import (
    add_payment_to_db, update_payment_status, add_user_to_db, 
    user_use_trial_to_db, check_user_trial, add_referral_to_db, 
    verify_referral, get_user_from_db
)
from app.keyboards import (
    main_menu, sub_menu, go_main_menu, get_payment_menu, 
    go_key_menu, get_key_menu, android_menu, ios_menu
)
from app.yoo_kassa import create_payment, check_payment

router = Router()
api = MarzbanAPI(base_url=MARZBAN_URL)



# --- Обработчики команд --- #

@router.message(CommandStart(deep_link=True))
async def handle_start_with_referral(message: Message, command: CommandObject):
    args = command.args
    if args:
        referral_user_id = str(message.from_user.id)
        referrer_user_id = decode_payload(args)

        if not await get_user_from_db(referral_user_id) and not await verify_referral(referral_user_id, use=False):
            await add_referral_to_db(referrer_user_id, referral_user_id)
            await message.answer(
                "🫂 Вы приглашены по реферальной ссылке!\n\n"
                "🎁 При покупке подписки — 7 бонусных дней бесплатно!"
            )
    await message.answer(main_text, reply_markup=main_menu, parse_mode=ParseMode.HTML)

@router.message(CommandStart())
async def handle_start(message: Message):
    await message.answer(main_text, reply_markup=main_menu, parse_mode=ParseMode.HTML)


# --- Кнопки --- #

@router.callback_query(F.data == 'sub')
async def handle_sub(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        '<b>Условия тарифа</b>\n'
        'Регион: Финляндия 🇫🇮\n'
        'Трафик: Безлимитный\n'
        'Устройства: до 2 одновременно\n\n'
        'Выберите срок подписки:',
        reply_markup=sub_menu,
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data == 'ref')
async def handle_referral(callback: CallbackQuery):
    from run import bot  # потенциально вынести наружу
    await callback.answer()
    user_id = str(callback.from_user.id)
    referral_link = await create_start_link(bot=bot, payload=user_id, encode=True)
    await callback.message.edit_text(
        "🎁 Пригласите друга и получите по 7 дней подписки в подарок!\n\n"
        f"🫂 Отправьте другу вашу реферальную ссылку: <code>{referral_link}</code>",
        reply_markup=go_main_menu,
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data == 'main_menu')
async def handle_main_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(main_text, reply_markup=main_menu, parse_mode=ParseMode.HTML)

@router.callback_query(F.data == 'connect_android')
async def handle_android(callback: CallbackQuery):
    await callback.answer()
    user_info = await get_user_info(callback)
    await callback.message.edit_text(
        connect_text('Android', 'Google Play'),
        reply_markup=await android_menu(user_info.subscription_url),
        parse_mode=ParseMode.HTML
    )

@router.callback_query(F.data == 'connect_ios')
async def handle_ios(callback: CallbackQuery):
    await callback.answer()
    user_info = await get_user_info(callback)
    await callback.message.edit_text(
        connect_text('iOS', 'App Store'),
        reply_markup=await ios_menu(user_info.subscription_url),
        parse_mode=ParseMode.HTML
    )


# --- Пробный период --- #

@router.callback_query(F.data == 'trial_5_days')
async def handle_trial(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    if await check_user_trial(user_id):
        await callback.answer('❌ Пробный период уже использован.', show_alert=True)
        return
    await callback.answer()
    await user_use_trial_to_db(user_id)
    await activate_subscription(callback, period=0, trial=True)


# --- Оплата --- #

@router.callback_query(F.data.startswith("sub_"))
async def handle_payment_request(callback: CallbackQuery):
    await callback.answer()
    user_id = str(callback.from_user.id)
    period = int(callback.data.split("_")[1])
    price = prices.get(period)
    payment_url, label, payment_yoo_id, status = await create_payment(price, user_id, period)
    await add_payment_to_db(label, user_id, price, status, payment_yoo_id)

    await callback.message.edit_text(
        f"💳 Оплатите подписку на {period} мес.\n\n"
        "После оплаты нажмите кнопку «Проверить платеж»",
        reply_markup=await get_payment_menu(payment_url, price, payment_yoo_id, period)
    )

@router.callback_query(F.data.startswith("check_payment_"))
async def handle_check_payment(callback: CallbackQuery):
    _, _, payment_yoo_id, period_str = callback.data.split("_")
    period = int(period_str)
    if await check_payment(payment_yoo_id):
        await update_payment_status("succeeded", payment_yoo_id)
        await activate_subscription(callback, period)
    else:
        await callback.answer('❌ Оплата не найдена. Попробуйте ещё проверить раз или обратитесь в поддержку.', show_alert=True)


# --- Подписка --- #

async def activate_subscription(callback: CallbackQuery, period: int = 0, trial: bool = False):
    user_id = str(callback.from_user.id)
    username = str(callback.from_user.username)
    token = await api.get_token(username=MARZBAN_USERNAME, password=MARZBAN_PASSWORD)

    try:
        user_info = await api.get_user(username=user_id, token=token.access_token)
        expiration_date = user_info.expire
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            user_info = None
            expiration_date = 0
        else:
            raise

    now = int(datetime.now().timestamp())
    add_time = 5 * 86400 if trial else period * 30 * 86400
    next_expire = max(expiration_date, now) + add_time

    if not user_info:
        await api.add_user(UserCreate(username=user_id, proxies={'vless': ProxySettings(flow='xtls-rprx-vision')},
                                      expire=next_expire, note=username), token=token.access_token)
    else:
        await api.modify_user(user_id, UserModify(expire=next_expire), token=token.access_token)

    # рефералка
    is_ref, referrer_user_id = await verify_referral(user_id, use=True)
    if is_ref:
        next_expire += 7 * 86400
        await api.modify_user(user_id, UserModify(expire=next_expire), token=token.access_token)

        referrer_info = await api.get_user(referrer_user_id, token=token.access_token)
        referrer_new_exp = max(referrer_info.expire, now) + 7 * 86400
        await api.modify_user(referrer_user_id, UserModify(expire=referrer_new_exp), token=token.access_token)
        await send_message_to_user(referrer_user_id)

    user_info = await api.get_user(user_id, token=token.access_token)
    await add_user_to_db(user_id, username, datetime.fromtimestamp(user_info.expire), trial)

    # текст
    if trial:
        text = '✅ Пробный период на 5 дней активирован!'
    elif is_ref:
        text = f'✅ Подписка активирована на {period} мес.\n🎁 +7 бонусных дней от друга!'
    else:
        text = f'✅ Подписка активирована на {period} мес.'

    await callback.message.edit_text(text, reply_markup=go_key_menu)


@router.callback_query(F.data == 'key')
async def handle_key(callback: CallbackQuery):
    user_info = await get_user_info(callback)
    if user_info:
        expire_date = datetime.fromtimestamp(user_info.expire)
        days_left = (expire_date - datetime.now()).days + 1
        if days_left < 0:
            await callback.message.edit_text('❌ Ваша подписка истекла.', reply_markup=go_main_menu)
        else:
            await callback.message.edit_text(
                f'🔑 Ваш ключ: <code>{user_info.subscription_url}</code>\n\n'
                f'📆 Подписка активна до: {expire_date.strftime("%d.%m.%Y")}\n'
                f'⏳ Осталось дней: {days_left}\n\n'
                '📱 Выберите устройство для подключения:',
                reply_markup=await get_key_menu(user_info.subscription_url),
                parse_mode=ParseMode.HTML
            )
    else:
        await callback.message.edit_text('❌ У вас нет активной подписки.', reply_markup=go_main_menu)


# --- Утилиты --- #

async def get_user_info(callback: CallbackQuery):
    user_id = str(callback.from_user.id)
    token = await api.get_token(username=MARZBAN_USERNAME, password=MARZBAN_PASSWORD)
    try:
        return await api.get_user(username=user_id, token=token.access_token)
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise
