import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------------- КНОПКИ ----------------
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🟢 Зарегистрировать команду")],
        [KeyboardButton(text="📄 Моя команда")]
    ],
    resize_keyboard=True
)

# ---------------- СОСТОЯНИЯ ----------------
class Form(StatesGroup):
    team = State()
    nicknames = State()
    username = State()

# ---------------- /start ----------------
@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer(
        "Добро пожаловать!\nВыберите действие:",
        reply_markup=menu
    )

# ---------------- НАЧАЛО РЕГИСТРАЦИИ ----------------
@dp.message(F.text == "🟢 Зарегистрировать команду")
async def reg_start(message: Message, state: FSMContext):
    await message.answer("Введите название команды:")
    await state.set_state(Form.team)

# ---------------- НАЗВАНИЕ КОМАНДЫ ----------------
@dp.message(Form.team)
async def get_team(message: Message, state: FSMContext):
    await state.update_data(team=message.text)
    await message.answer("Введите никнеймы игроков:")
    await state.set_state(Form.nicknames)

# ---------------- НИКНЕЙМЫ ----------------
@dp.message(Form.nicknames)
async def get_nicknames(message: Message, state: FSMContext):
    await state.update_data(nicknames=message.text)
    await message.answer("Введите юзернейм регистратора:")
    await state.set_state(Form.username)

# ---------------- ФИНИШ ----------------
@dp.message(Form.username)
async def finish(message: Message, state: FSMContext):
    data = await state.get_data()
    username = message.text

    text = (
        f"📥 НОВАЯ КОМАНДА\n\n"
        f"🏷 Команда: {data['team']}\n"
        f"👥 Никнеймы: {data['nicknames']}\n"
        f"👤 Регистратор: @{username}"
    )

    # админу
    await bot.send_message(ADMIN_ID, text)

    # пользователю
    await message.answer("✅ Ваша команда успешно зарегистрирована!", reply_markup=menu)

    await state.clear()

# ---------------- "МОЯ КОМАНДА" (заглушка) ----------------
@dp.message(F.text == "📄 Моя команда")
async def my_team(message: Message):
    await message.answer("ℹ️ Эта функция будет добавлена позже (по желанию можем сделать базу данных).")

# ---------------- RUN ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())