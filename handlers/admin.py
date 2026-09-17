import asyncio
from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS, STORAGE_CHANNEL_ID
from states import AdminState
from database import db
from keyboards import admin_main_keyboard, cancel_keyboard, user_main_keyboard

router = Router()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Boshqaruv paneli:", reply_markup=admin_main_keyboard)

@router.message(F.text == "🔙 Bosh menyuga qaytish")
async def btn_back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Bosh menyu:", reply_markup=user_main_keyboard)

@router.message(F.text == "🚫 Bekor qilish")
async def btn_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Amal bekor qilindi.", reply_markup=admin_main_keyboard)

# --- ANIME QO'SHISH ---
@router.message(F.text == "🎬 Anime qo'shish")
async def add_anime_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Yangi anime uchun kod kiriting (masalan: 105):", reply_markup=cancel_keyboard)
    await state.set_state(AdminState.add_anime_code)

@router.message(AdminState.add_anime_code)
async def add_anime_code(message: Message, state: FSMContext):
    await state.update_data(code=message.text.strip())
    await message.answer("Endi anime videosini yuboring (Ombor kanalga avto yuklanadi):", reply_markup=cancel_keyboard)
    await state.set_state(AdminState.add_anime_file)

@router.message(AdminState.add_anime_file, F.video)
async def add_anime_file(message: Message, state: FSMContext, bot: Bot):
    file_id = message.video.file_id
    if STORAGE_CHANNEL_ID != 0:
        sent_msg = await bot.send_video(chat_id=STORAGE_CHANNEL_ID, video=file_id, caption=f"KOD: {message.text}")
        file_id = sent_msg.video.file_id

    await state.update_data(file_id=file_id)
    await message.answer("Anime nomini yoki qisqacha tavsifini kiriting:", reply_markup=cancel_keyboard)
    await state.set_state(AdminState.add_anime_title)

@router.message(AdminState.add_anime_title)
async def add_anime_title(message: Message, state: FSMContext):
    data = await state.get_data()
    await db.add_anime(code=data['code'], file_id=data['file_id'], title=message.text)
    await state.clear()
    await message.answer(f"✅ Anime kodi ({data['code']}) saqlandi!", reply_markup=admin_main_keyboard)

# --- MAJBURIY OBUNA KANAL QO'SHISH/O'CHIRISH ---
@router.message(F.text == "➕ Kanal qo'shish")
async def add_channel_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Kanal ID sini yuboring (Masalan: -1001234567890):", reply_markup=cancel_keyboard)
    await state.set_state(AdminState.add_channel_id)

@router.message(AdminState.add_channel_id)
async def add_channel_id(message: Message, state: FSMContext):
    try:
        ch_id = int(message.text.strip())
        await state.update_data(ch_id=ch_id)
        await message.answer("Kanalga taklif havolasini (link) yuboring:", reply_markup=cancel_keyboard)
        await state.set_state(AdminState.add_channel_url)
    except ValueError:
        await message.answer("Noto'g'ri ID. Faqat raqam yuboring:")

@router.message(AdminState.add_channel_url)
async def add_channel_url(message: Message, state: FSMContext):
    data = await state.get_data()
    await db.add_channel(data['ch_id'], message.text.strip())
    await state.clear()
    await message.answer("✅ Kanal ro'yxatga qo'shildi!", reply_markup=admin_main_keyboard)

@router.message(F.text == "➖ Kanal o'chirish")
async def del_channel_start(message: Message):
    if not is_admin(message.from_user.id):
        return
    channels = await db.get_channels()
    if not channels:
        await message.answer("Hech qanday kanal topilmadi.", reply_markup=admin_main_keyboard)
        return
    
    text = "O'chirmoqchi bo'lgan kanal ID sini tanlab, nusxalab oling:\n\n"
    for ch_id, link in channels:
        text += f"ID: `{ch_id}` | Link: {link}\n"
    await message.answer(text, parse_mode="Markdown", reply_markup=admin_main_keyboard)

# --- XABAR TARQATISH ---
@router.message(F.text == "📢 Xabar yuborish")
async def broadcast_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await message.answer("Barcha foydalanuvchilarga yuboriladigan xabarni kiriting (Matn, Rasm yoki Video):", reply_markup=cancel_keyboard)
    await state.set_state(AdminState.broadcast)

@router.message(AdminState.broadcast)
async def broadcast_send(message: Message, state: FSMContext, bot: Bot):
    users = await db.get_all_users()
    count = 0
    await message.answer(f"🚀 Xabar {len(users)} ta foydalanuvchiga yuborilmoqda...")
    
    for u in users:
        try:
            await bot.copy_message(chat_id=u['user_id'], from_chat_id=message.chat.id, message_id=message.message_id)
            count += 1
            await asyncio.sleep(0.05)
        except Exception:
            pass
            
    await state.clear()
    await message.answer(f"✅ Xabar {count} ta foydalanuvchiga muvaffaqiyatli yetkazildi!", reply_markup=admin_main_keyboard)
