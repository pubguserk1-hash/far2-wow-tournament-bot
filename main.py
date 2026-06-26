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

# ---------------- ПАМЯТЬ ----------------
registered_users = set()   # 🔐 1 заявка на пользователя
user_to_team = {}          # для уведомлений

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

    # 🔐 ОГРАНИЧЕНИЕ 1 ЗАЯВКИ
    if message.from_user.id in registered_users:
        await message.answer("❌ Вы уже отправили заявку!")
        return

    await message.answer("Введите название команды:")
    await state.set_state(Form.team)

# ---------------- КОМАНДА ----------------
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

# ---------------- ФИНАЛ ----------------
@dp.message(Form.username)
async def finish(message: Message, state: FSMContext):
    data = await state.get_data()
    username = message.text.strip()

    user_id = message.from_user.id
    team = data["team"]

    registered_users.add(user_id)
    user_to_team[user_id] = team

    text = (
        f"📥 НОВАЯ ЗАЯВКА\n\n"
        f"🏷 Команда: {team}\n"
        f"👥 Никнеймы: {data['nicknames']}\n"
        f"👤 Регистратор: @{username}\n"
        f"🆔 UserID: {user_id}"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept|{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject|{user_id}")
        ]
    ])

    await bot.send_message(ADMIN_ID, text, reply_markup=kb)
    await message.answer("✅ Заявка отправлена!", reply_markup=menu)

    await state.clear()

# ---------------- ПРИНЯТЬ ----------------
@dp.callback_query(F.data.startswith("accept"))
async def accept(call: CallbackQuery):
    user_id = int(call.data.split("|")[1])

    team = user_to_team.get(user_id, "Неизвестно")

    await bot.send_message(user_id, f"✅ Ваша заявка на команду '{team}' ПРИНЯТА!")

    await call.message.edit_text(call.message.text + "\n\n✅ ПРИНЯТО")
    await call.answer("Принято")

# ---------------- ОТКЛОНИТЬ ----------------
@dp.callback_query(F.data.startswith("reject"))
async def reject(call: CallbackQuery):
    user_id = int(call.data.split("|")[1])

    team = user_to_team.get(user_id, "Неизвестно")

    registered_users.discard(user_id)

    await bot.send_message(user_id, f"❌ Ваша заявка на команду '{team}' ОТКЛОНЕНА!")

    await call.message.edit_text(call.message.text + "\n\n❌ ОТКЛОНЕНО")
    await call.answer("Отклонено")

# ---------------- RUN ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())