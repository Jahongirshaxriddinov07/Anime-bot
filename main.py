import asyncio
import os
from aiogram import Bot, Dispatcher
from aiohttp import web

from config import BOT_TOKEN
from database import db
from handlers import user, admin

# Render uxlab qolmasligi uchun kichik veb-server
async def handle_ping(request):
    return web.Response(text="Bot is active!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    # Baza ulash
    await db.connect()

    # Routerlarni ulash
    dp.include_router(admin.router)
    dp.include_router(user.router)

    # Veb-serverni parallel ravishda ishga tushirish
    asyncio.create_task(start_web_server())

    print("Bot muvaffaqiyatli ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
