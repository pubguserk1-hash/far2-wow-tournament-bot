
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

# ---------------- DB ----------------
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

# ---------------- USER MENU ----------------
menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🟢 Зарегистрировать команду")],
        [KeyboardButton(text="📄 Моя команда")],
        [KeyboardButton(text="❌ Снять команду")]
    ],
    resize_keyboard=True
)

# ---------------- ADMIN MENU ----------------
admin_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="👑 Админ-панель")]
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
    if message.from_user.id == ADMIN_ID:
        await message.answer("👑 Админ вход", reply_markup=admin_menu)
    else:
        await message.answer("Выберите действие:", reply_markup=menu)

# ---------------- ADMIN PANEL ----------------
@dp.message(F.text == "👑 Админ-панель")
async def admin_panel(message: Message):

    if message.from_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT COUNT(*) FROM teams")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM teams WHERE status='pending'")
    pending = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM teams WHERE status='accepted'")
    accepted = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM teams WHERE status='rejected'")
    rejected = cursor.fetchone()[0]

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Все команды", callback_data="all")],
        [InlineKeyboardButton(text="⏳ Ожидают", callback_data="pending")],
        [InlineKeyboardButton(text="✅ Принятые", callback_data="accepted")],
        [InlineKeyboardButton(text="❌ Отклонённые", callback_data="rejected")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="stats")]
    ])

    await message.answer(
        f"👑 АДМИН-ПАНЕЛЬ\n\n"
        f"📊 Всего: {total}\n"
        f"⏳ Ожидают: {pending}\n"
        f"✅ Приняты: {accepted}\n"
        f"❌ Отклонены: {rejected}",
        reply_markup=kb
    )

# ---------------- CALLBACK MENU ----------------
@dp.callback_query(F.data.in_(["all","pending","accepted","rejected"]))
async def show_lists(call: CallbackQuery):

    query_map = {
        "all": "SELECT user_id, team, status FROM teams",
        "pending": "SELECT user_id, team, status FROM teams WHERE status='pending'",
        "accepted": "SELECT user_id, team, status FROM teams WHERE status='accepted'",
        "rejected": "SELECT user_id, team, status FROM teams WHERE status='rejected'",
    }

    cursor.execute(query_map[call.data])
    rows = cursor.fetchall()

    if not rows:
        await call.message.edit_text("📭 Пусто")
        return

    text = "📋 СПИСОК КОМАНД:\n\n"

    kb = []

    for user_id, team, status in rows:
        text += f"🏷 {team} | {status}\n"

        kb.append([
            InlineKeyboardButton(text=f"🏷 {team}", callback_data=f"view|{user_id}")
        ])

    await call.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))

# ---------------- VIEW TEAM ----------------
@dp.callback_query(F.data.startswith("view"))
async def view_team(call: CallbackQuery):

    user_id = int(call.data.split("|")[1])

    cursor.execute("SELECT team, nicknames, username, status FROM teams WHERE user_id=?", (user_id,))
    row = cursor.fetchone()

    if not row:
        await call.answer("Не найдено")
        return

    team, nicknames, username, status = row

    text = (
        f"🏷 {team}\n"
        f"👥 {nicknames}\n"
        f"👤 @{username}\n"
        f"📊 {status}"
    )

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять", callback_data=f"accept|{user_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject|{user_id}")
        ],
        [
            InlineKeyboardButton(text="🗑 Удалить", callback_data=f"delete|{user_id}")
        ]
    ])

    await call.message.edit_text(text, reply_markup=kb)

# ---------------- ACCEPT ----------------
@dp.callback_query(F.data.startswith("accept"))
async def accept(call: CallbackQuery):
    user_id = int(call.data.split("|")[1])

    cursor.execute("UPDATE teams SET status='accepted' WHERE user_id=?", (user_id,))
    conn.commit()

    await bot.send_message(user_id, "✅ Ваша команда ПРИНЯТА!")

    await call.answer("Принято")

# ---------------- REJECT ----------------
@dp.callback_query(F.data.startswith("reject"))
async def reject(call: CallbackQuery):
    user_id = int(call.data.split("|")[1])

    cursor.execute("UPDATE teams SET status='rejected' WHERE user_id=?", (user_id,))
    conn.commit()

    await bot.send_message(user_id, "❌ Ваша команда ОТКЛОНЕНА!")

    await call.answer("Отклонено")

# ---------------- DELETE ----------------
@dp.callback_query(F.data.startswith("delete"))
async def delete(call: CallbackQuery):
    user_id = int(call.data.split("|")[1])

    cursor.execute("DELETE FROM teams WHERE user_id=?", (user_id,))
    conn.commit()

    await bot.send_message(user_id, "⚠️ Ваша команда была удалена админом")
    await call.answer("Удалено")

# ---------------- USER REGISTRATION ----------------
@dp.message(F.text == "🟢 Зарегистрировать команду")
async def reg_start(message: Message, state: FSMContext):

    cursor.execute("SELECT * FROM teams WHERE user_id=?", (message.from_user.id,))
    if cursor.fetchone():
        await message.answer("❌ Уже есть команда")
        return

    await message.answer("Введите название команды:")
    await state.set_state(Form.team)

@dp.message(Form.team)
async def get_team(message: Message, state: FSMContext):
    team = message.text.strip()

    cursor.execute("SELECT * FROM teams WHERE team=?", (team,))
    if cursor.fetchone():
        await message.answer("❌ Уже существует")
        return

    await state.update_data(team=team)
    await message.answer("Введите никнеймы через пробел:")
    await state.set_state(Form.nicknames)

@dp.message(Form.nicknames)
async def get_nicknames(message: Message, state: FSMContext):
    await state.update_data(nicknames=message.text)
    await message.answer("Введите юзернейм без "@":")
    await state.set_state(Form.username)

@dp.message(Form.username)
async def finish(message: Message, state: FSMContext):

    data = await state.get_data()

    cursor.execute("""
        INSERT INTO teams (user_id, team, nicknames, username, status)
        VALUES (?, ?, ?, ?, 'pending')
    """, (message.from_user.id, data["team"], data["nicknames"], message.text))

    conn.commit()

    await message.answer("✅ Отправлено!", reply_markup=menu)
    await state.clear()

# ---------------- MY TEAM ----------------
@dp.message(F.text == "📄 Моя команда")
async def my_team(message: Message):

    cursor.execute("SELECT team, nicknames, username, status FROM teams WHERE user_id=?",
                   (message.from_user.id,))
    row = cursor.fetchone()

    if not row:
        await message.answer("❌ Нет команды")
        return

    team, nicknames, username, status = row

    await message.answer(
        f"🏷 {team}\n👥 {nicknames}\n👤 @{username}\n📊 {status}"
    )

# ---------------- REMOVE ----------------
@dp.message(F.text == "❌ Снять команду")
async def remove(message: Message):

    cursor.execute("SELECT team FROM teams WHERE user_id=?", (message.from_user.id,))
    row = cursor.fetchone()

    if not row:
        await message.answer("❌ Нет команды")
        return

    team = row[0]

    cursor.execute("DELETE FROM teams WHERE user_id=?", (message.from_user.id,))
    conn.commit()

    await bot.send_message(ADMIN_ID, f"⚠️ Команда снята: {team}")

    await message.answer("✅ Удалено")

# ---------------- RUN ----------------
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())