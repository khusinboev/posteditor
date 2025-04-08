from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from config import admin

# Bot tokenini shu yerga yozing
BOT_TOKEN = "8087409160:AAFI_fNDhesvlcRCzDrcRo4tyk5aaYZPGkE"

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
        await message.answer("Boshlandi.")

# /stop komandasi uchun handler
@dp.message(Command("stop"))
async def cmd_stop(message: types.Message):
    if message.chat.id in admin:
        # data.txt fayliga /stop yozish
        with open("data.txt", "w") as file:
            file.write("/stop")
        await message.answer("To'xtadi.")

# Asosiy funksiya
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())