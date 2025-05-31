from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import TELEGRAPH_TERMS, TELETYPE_INSTRUCTION, VPN_CONNECT_TEMPLATE

# Главное меню
main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🎁 Пробный период (5 дней)", callback_data="trial_5_days")],
    [InlineKeyboardButton(text="💳 Оформить подписку", callback_data="sub")],
    [InlineKeyboardButton(text="🔑 Мой ключ | Подключиться", callback_data="key")],
    [InlineKeyboardButton(text="🫂 Реферальная ссылка", callback_data="ref")],
    [InlineKeyboardButton(text="ℹ️ Условия", url=TELEGRAPH_TERMS),
     InlineKeyboardButton(text="⚙️ Инструкция", url=TELETYPE_INSTRUCTION)],
])

# Меню подписок
sub_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="1 месяц ‒ 99 ₽", callback_data="sub_1")],
    [InlineKeyboardButton(text="3 месяца ‒ 299 ₽", callback_data="sub_3")],
    [InlineKeyboardButton(text="6 месяцев ‒ 599 ₽", callback_data="sub_6")],
    [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")],
])

# Возврат в меню
go_main_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="⬅️ На главную", callback_data="main_menu")]
])

go_key_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛡️ Подключиться", callback_data="key")]
])

# 💳 Меню оплаты
async def get_payment_menu(url: str, price: int, payment_yoo_id: str, period: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💳 Оплатить по СБП {price} ₽", url=url)],
        [InlineKeyboardButton(text="🔄 Проверить платеж", callback_data=f"check_payment_{payment_yoo_id}_{period}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="sub")]
    ])

# Меню подключения
async def get_key_menu(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🤖 Android", callback_data="connect_android"),
            InlineKeyboardButton(text="🍏 iOS", callback_data="connect_ios"),
        ],
        [InlineKeyboardButton(text="💻 Windows & macOS", url=TELETYPE_INSTRUCTION)],
        [InlineKeyboardButton(text="⚙️ Инструкция", url=TELETYPE_INSTRUCTION)],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="main_menu")]
    ])

async def android_menu(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Скачать приложение", url="https://play.google.com/store/apps/details?id=com.v2raytun.android&hl=ru")],
        [InlineKeyboardButton(text="🛡️ Подключиться", url=VPN_CONNECT_TEMPLATE.format(url))],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="key")]
    ])

async def ios_menu(url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Скачать приложение", url="https://apps.apple.com/us/app/v2raytun/id6476628951")],
        [InlineKeyboardButton(text="🛡️ Подключиться", url=VPN_CONNECT_TEMPLATE.format(url))],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="key")]
    ])
