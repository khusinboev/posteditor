from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import admin, BOT_TOKEN
from logging_setup import setup_logging
import logging

setup_logging()
logger = logging.getLogger("posteditor.bot")

# Bot va dispatcher yaratish
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# /start komandasi uchun handler
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if message.chat.id in admin:
        # data.txt fayliga /start yozish
        with open("data.txt", "w") as file:
            file.write("/start")
        logger.info("/start qabul qilindi: %s", message.chat.id)
        await message.answer("Boshlandi.")

# /stop komandasi uchun handler
@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
    if message.chat.id in admin:
        # data.txt fayliga /stop yozish
        with open("data.txt", "w") as file:
            file.write("/stop")
        logger.info("/stop qabul qilindi: %s", message.chat.id)
        await message.answer("To'xtadi.")

# Asosiy funksiya
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())