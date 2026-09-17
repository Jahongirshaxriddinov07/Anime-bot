from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.enums import ChatMemberStatus

from states import Registration
from database import db
from keyboards import phone_keyboard, user_main_keyboard, get_subscription_keyboard

router = Router()

async def check_user_sub(bot: Bot, user_id: int) -> bool:
    channels = await db.get_channels()
    for ch_id, link in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch_id, user_id=user_id)
            if member.status in [ChatMemberStatus.LEFT, ChatMemberStatus.KICKED]:
                return False
        except Exception:
            pass
    return True

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    is_registered = await db.is_registered(message.from_user.id)
    if not is_registered:
        await message.answer(
            "Assalomu alaykum! Botdan foydalanish uchun ro'yxatdan o'ting.\n\nIsmingizni kiriting:",
            reply_markup=None
        )
        await state.set_state(Registration.name)
        return

    is_sub = await check_user_sub(bot, message.from_user.id)
    if not is_sub:
        channels = await db.get_channels()
        await message.answer(
            "Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:",
            reply_markup=get_subscription_keyboard(channels)
        )
        return

    await message.answer("Xush kelibsiz! Anime kodini yuboring yoki menudan foydalaning:", reply_markup=user_main_keyboard)

@router.message(Registration.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Endi pastdagi tugma orqali telefon raqamingizni yuboring:", reply_markup=phone_keyboard)
    await state.set_state(Registration.phone)

@router.message(Registration.phone, F.contact)
async def process_phone(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    phone = message.contact.phone_number
    await db.add_user(message.from_user.id, data['name'], phone)
    await state.clear()
    
    await message.answer("Ro'yxatdan muvaffaqiyatli o'tdingiz!", reply_markup=user_main_keyboard)
    
    is_sub = await check_user_sub(bot, message.from_user.id)
    if not is_sub:
        channels = await db.get_channels()
        await message.answer(
            "Botdan foydalanish uchun kanallarga obuna bo'ling:",
            reply_markup=get_subscription_keyboard(channels)
        )

@router.callback_query(F.data == "check_sub")
async def process_check_sub(callback: CallbackQuery, bot: Bot):
    is_sub = await check_user_sub(bot, callback.from_user.id)
    if is_sub:
        await callback.message.delete()
        await callback.message.answer("Obuna tasdiqlandi! Anime kodini yuborishingiz mumkin.", reply_markup=user_main_keyboard)
    else:
        await callback.answer("Hali hamma kanallarga obuna bo'lmadingiz!", show_alert=True)

@router.message(F.text == "🔍 Anime qidirish")
async def btn_search(message: Message):
    await message.answer("Anime kodini yuboring (Masalan: 105):")

@router.message(F.text == "📊 Statistika")
async def btn_stats(message: Message):
    users = await db.get_all_users()
    await message.answer(f"📊 Botimizdan foydalanuvchilar soni: {len(users)} ta")

@router.message(F.text)
async def process_anime_code(message: Message, bot: Bot):
    is_sub = await check_user_sub(bot, message.from_user.id)
    if not is_sub:
        channels = await db.get_channels()
        await message.answer(
            "Botdan foydalanish uchun kanallarga obuna bo'ling:",
            reply_markup=get_subscription_keyboard(channels)
        )
        return

    code = message.text.strip()
    anime = await db.get_anime(code)
    if anime:
        await message.answer_video(video=anime['file_id'], caption=f"🎬 Anime: {anime['title']}\n🔑 Kodi: {code}")
    else:
        await message.answer("❌ Bu kod bo'yicha hech qanday anime topilmadi.")
