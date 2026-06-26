import asyncio
import os
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------------- DB ----------------
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    team TEXT UNIQUE,
    nicknames TEXT,
    username TEXT
)
""")
conn.commit()

# ---------------- КНОПКИ ----------------
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🟢 Зарегистрировать команду")],
        [KeyboardButton(text="📄 Моя команда")]
    ],
    resize_keyboard=True
)

# ---------------- STATES ----------------
class Form(StatesGroup):
    team = State()
    nicknames = State()
    username = State()

# ---------------- START ----------------
@dp.message(F.text == "/start")
async def start(message: Message):
    await message.answer("Выберите действие:", reply_markup=menu)

# ---------------- REG START ----------------
@dp.message(F.text == "🟢 Зарегистрировать команду")
async def reg_start(message: Message, state: FSMContext):

    # проверка в БД
    cursor.execute("SELECT * FROM teams WHERE user_id=?", (message.from_user.id,))
    if cursor.fetchone():
        await message.answer("❌ У вас уже есть зарегистрированная команда!")
        return

    await message.answer("Введите название команды:")
    await state.set_state(Form.team)

# ---------------- TEAM ----------------
@dp.message(Form.team)
async def get_team(message: Message, state: FSMContext):
    team = message.text.strip()

    # проверка уникальности команды
    cursor.execute("SELECT * FROM teams WHERE team=?", (team,))
    if cursor.fetchone():
        await message.answer("❌ Такая команда уже существует!")
        return

    await state.update_data(team=team)
    await message.answer("Введите никнеймы игроков:")
    await state.set_state(Form.nicknames)

# ---------------- NICKNAMES ----------------
@dp.message(Form.nicknames)
async def get_nicknames(message: Message, state: FSMContext):
    await state.update_data(nicknames=message.text)
    await message.answer("Введите юзернейм регистратора:")
    await state.set_state(Form.username)

# ---------------- FINISH ----------------
@dp.message(Form.username)
async def finish(message: Message, state: FSMContext):
    data = await state.get_data()

    team = data["team"]
    nicknames = data["nicknames"]
    username = message.text
    user_id = message.from_user.id

    # сохранить в БД
    cursor.execute(
        "INSERT INTO teams (user_id, team, nicknames, username) VALUES (?, ?, ?, ?)",
        (user_id, team, nicknames, username)
    )
    conn.commit()

    text = (
        f"📥 НОВАЯ КОМАНДА\n\n"
        f"🏷 {team}\n"
        f"👥 {nicknames}\n"
        f"👤 @{username}\n"
        f"🆔 {user_id}"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept|{user_id}|{team}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject|{user_id}|{team}")
        ]
    ])

    await bot.send_message(ADMIN_ID, text, reply_markup=kb)
    await message.answer("✅ Заявка отправлена!", reply_markup=menu)

    await state.clear()

# ---------------- ADMIN LIST ----------------
@dp.message(F.text == "/list")
async def list_teams(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT team, nicknames, username FROM teams")
    rows = cursor.fetchall()

    if not rows:
        await message.answer("📭 Нет команд")
        return

    text = "📋 СПИСОК КОМАНД:\n\n"
    for i, r in enumerate(rows, 1):
        text += f"{i}. 🏷 {r[0]} | 👥 {r[1]} | 👤 {r[2]}\n"

    await message.answer(text)

# ---------------- BAN ----------------
@dp.message(F.text.startswith("/ban"))
async def ban_team(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    try:
        team = message.text.split(" ", 1)[1]
    except:
        await message.answer("❌ Используй: /ban <название команды>")
        return

    cursor.execute("DELETE FROM teams WHERE team=?", (team,))
    conn.commit()

    await message.answer(f"❌ Команда {team} удалена")

# ---------------- CALLBACKS ----------------
@dp.callback_query(F.data.startswith("accept"))
async def accept(call: CallbackQuery):
    _, user_id, team = call.data.split("|")

    await bot.send_message(int(user_id), f"✅ Ваша команда '{team}' ПРИНЯТА!")
    await call.message.edit_text(call.message.text + "\n\n✅ ПРИНЯТО")

# ---------------- REJECT ----------------
@dp.callback_query(F.data.startswith("reject"))
async def reject(call: CallbackQuery):
    _, user_id, team = call.data.split("|")

    cursor.execute("DELETE FROM teams WHERE team=?", (team,))
    conn.commit()

    await bot.send_message(int(user_id), f"❌ Ваша команда '{team}' ОТКЛОНЕНА!")
    await call.message.edit_text(call.message.text + "\n\n❌ ОТКЛОНЕНО")

# ---------------- RUN ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())