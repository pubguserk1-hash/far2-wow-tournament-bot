import asyncio
import os
import sqlite3

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ---------------- DATABASE ----------------
conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS teams (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE,
    team TEXT UNIQUE,
    nicknames TEXT,
    username TEXT,
    status TEXT DEFAULT 'pending'
)
""")
conn.commit()

# ---------------- KEYBOARD ----------------
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🟢 Зарегистрировать команду")],
        [KeyboardButton(text="📄 Моя команда")],
        [KeyboardButton(text="❌ Снять команду")]
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

# ---------------- REGISTER START ----------------
@dp.message(F.text == "🟢 Зарегистрировать команду")
async def reg_start(message: Message, state: FSMContext):

    cursor.execute("SELECT * FROM teams WHERE user_id=?", (message.from_user.id,))
    if cursor.fetchone():
        await message.answer("❌ У вас уже есть команда!")
        return

    await message.answer("Введите название команды:")
    await state.set_state(Form.team)

# ---------------- TEAM ----------------
@dp.message(Form.team)
async def get_team(message: Message, state: FSMContext):
    team = message.text.strip()

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

    user_id = message.from_user.id
    team = data["team"]
    nicknames = data["nicknames"]
    username = message.text.strip()

    cursor.execute("""
        INSERT INTO teams (user_id, team, nicknames, username, status)
        VALUES (?, ?, ?, ?, 'pending')
    """, (user_id, team, nicknames, username))
    conn.commit()

    text = (
        f"📥 НОВАЯ ЗАЯВКА\n\n"
        f"🏷 {team}\n"
        f"👥 {nicknames}\n"
        f"👤 @{username}\n"
        f"🆔 {user_id}"
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

# ---------------- MY TEAM ----------------
@dp.message(F.text == "📄 Моя команда")
async def my_team(message: Message):

    cursor.execute("""
        SELECT team, nicknames, username, status
        FROM teams WHERE user_id=?
    """, (message.from_user.id,))
    row = cursor.fetchone()

    if not row:
        await message.answer("❌ У вас нет команды")
        return

    team, nicknames, username, status = row

    status_text = {
        "pending": "⏳ На рассмотрении",
        "accepted": "✅ Принята",
        "rejected": "❌ Отклонена"
    }.get(status, "❓")

    await message.answer(
        f"📄 ВАША КОМАНДА\n\n"
        f"🏷 {team}\n"
        f"👥 {nicknames}\n"
        f"👤 @{username}\n"
        f"📊 {status_text}"
    )

# ---------------- REMOVE TEAM ----------------
@dp.message(F.text == "❌ Снять команду")
async def remove_team(message: Message):

    user_id = message.from_user.id

    cursor.execute("SELECT team FROM teams WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if not row:
        await message.answer("❌ У вас нет команды")
        return

    team = row[0]

    cursor.execute("DELETE FROM teams WHERE user_id=?", (user_id,))
    conn.commit()

    # уведомление админу
    await bot.send_message(
        ADMIN_ID,
        f"⚠️ КОМАНДА СНЯТА\n\n🏷 {team}\n👤 UserID: {user_id}"
    )

    await message.answer("✅ Ваша команда снята с регистрации")

# ---------------- ADMIN LIST ----------------
@dp.message(F.text == "/list")
async def list_teams(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT team, status FROM teams")
    rows = cursor.fetchall()

    text = "📋 КОМАНДЫ:\n\n"
    for i, r in enumerate(rows, 1):
        text += f"{i}. {r[0]} | {r[1]}\n"

    await message.answer(text)

# ---------------- BAN ----------------
@dp.message(F.text.startswith("/ban"))
async def ban(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    try:
        team = message.text.split(" ", 1)[1]
    except:
        await message.answer("❌ /ban <team>")
        return

    cursor.execute("DELETE FROM teams WHERE team=?", (team,))
    conn.commit()

    await message.answer(f"❌ {team} удалена")

# ---------------- ACCEPT ----------------
@dp.callback_query(F.data.startswith("accept"))
async def accept(call: CallbackQuery):
    user_id = int(call.data.split("|")[1])

    cursor.execute("UPDATE teams SET status='accepted' WHERE user_id=?", (user_id,))
    conn.commit()

    await bot.send_message(user_id, "✅ Ваша команда ПРИНЯТА!")
    await call.message.edit_text(call.message.text + "\n\n✅ ПРИНЯТО")

# ---------------- REJECT ----------------
@dp.callback_query(F.data.startswith("reject"))
async def reject(call: CallbackQuery):
    user_id = int(call.data.split("|")[1])

    cursor.execute("UPDATE teams SET status='rejected' WHERE user_id=?", (user_id,))
    conn.commit()

    await bot.send_message(user_id, "❌ Ваша команда ОТКЛОНЕНА!")
    await call.message.edit_text(call.message.text + "\n\n❌ ОТКЛОНЕНО")

# ---------------- RUN ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())