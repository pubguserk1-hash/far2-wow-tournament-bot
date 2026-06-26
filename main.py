import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "Отправьте пожалуйста:\n"
        "Название команды | никнеймы | юзернейм кто регистрирует"
    )

@dp.message()
async def get_data(message: Message):
    text = message.text

    await bot.send_message(
        ADMIN_ID,
        f"📥 Новая регистрация:\n\n{text}\n\nОт: @{message.from_user.username}"
    )

    await message.answer("✅ Ваша команда успешно зарегистрирована")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())