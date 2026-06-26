import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------------- ПАМЯТЬ (анти-дубликаты) ----------------
registered_teams = set()

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
    await message.answer("Выберите действие:", reply_markup=menu)

# ---------------- СТАРТ ----------------
@dp.message(F.text == "🟢 Зарегистрировать команду")
async def reg_start(message: Message, state: FSMContext):
    await message.answer("Введите название команды:")
    await state.set_state(Form.team)

# ---------------- КОМАНДА ----------------
@dp.message(Form.team)
async def get_team(message: Message, state: FSMContext):
    team = message.text.strip()

    # ❌ АНТИ-ДУБЛИКАТ
    if team.lower() in registered_teams:
        await message.answer("❌ Эта команда уже зарегистрирована!")
        return

    await state.update_data(team=team)
    await message.answer("Введите никнеймы игроков:")
    await state.set_state(Form.nicknames)

# ---------------- НИКНЕЙМЫ ----------------
@dp.message(Form.nicknames)
async def get_nicknames(message: Message, state: FSMContext):
    await state.update_data(nicknames=message.text)
    await message.answer("Введите юзернейм регистратора:")
    await state.set_state(Form.username)

# ---------------- ФИНАЛ ----------------
@dp.message(Form.username)
async def finish(message: Message, state: FSMContext):
    data = await state.get_data()
    username = message.text.strip()

    team = data["team"]
    registered_teams.add(team.lower())

    text = (
        f"📥 НОВАЯ ЗАЯВКА\n\n"
        f"🏷 Команда: {team}\n"
        f"👥 Никнеймы: {data['nicknames']}\n"
        f"👤 Регистратор: @{username}"
    )

    # админ-кнопки
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept|{team}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject|{team}")
        ]
    ])

    await bot.send_message(ADMIN_ID, text, reply_markup=kb)
    await message.answer("✅ Заявка отправлена!", reply_markup=menu)

    await state.clear()

# ---------------- АДМИН: ПРИЕМ ----------------
@dp.callback_query(F.data.startswith("accept"))
async def accept(call: CallbackQuery):
    team = call.data.split("|")[1]

    await call.message.edit_text(
        call.message.text + "\n\n✅ ПРИНЯТО"
    )

    await call.answer("Принято")

# ---------------- АДМИН: ОТКЛОН ----------------
@dp.callback_query(F.data.startswith("reject"))
async def reject(call: CallbackQuery):
    team = call.data.split("|")[1]

    registered_teams.discard(team.lower())

    await call.message.edit_text(
        call.message.text + "\n\n❌ ОТКЛОНЕНО"
    )

    await call.answer("Отклонено")

# ---------------- RUN ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())