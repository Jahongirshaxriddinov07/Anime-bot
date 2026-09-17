from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Telefon raqam yuborish tugmasi
phone_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True
)

# Foydalanuvchi Bosh menyusi
user_main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Anime qidirish")],
        [KeyboardButton(text="📊 Statistika")]
    ],
    resize_keyboard=True
)

# Admin Paneli menyusi
admin_main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎬 Anime qo'shish"), KeyboardButton(text="📢 Xabar yuborish")],
        [KeyboardButton(text="➕ Kanal qo'shish"), KeyboardButton(text="➖ Kanal o'chirish")],
        [KeyboardButton(text="🔙 Bosh menyuga qaytish")]
    ],
    resize_keyboard=True
)

# Bekor qilish tugmasi (Forma to'ldirish paytida)
cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🚫 Bekor qilish")]
    ],
    resize_keyboard=True
)

# Majburiy obuna tugmalarini shakllantirish
def get_subscription_keyboard(channels: list) -> InlineKeyboardMarkup:
    buttons = []
    for idx, (ch_id, link) in enumerate(channels, 1):
        buttons.append([InlineKeyboardButton(text=f"➕ {idx}-Kanalga obuna bo'lish", url=link)])
    buttons.append([InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)
