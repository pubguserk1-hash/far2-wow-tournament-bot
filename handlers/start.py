from telegram import Update
from telegram.ext import ContextTypes

from keyboards import main_menu

from database import teams_count

from config import (
    ADMIN_IDS,
    TOURNAMENT_NAME,
    PRIZE
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user

    text = f"""
🏆 <b>{TOURNAMENT_NAME}</b>

🎁 <b>Призовой фонд:</b>

{PRIZE}

👥 Зарегистрировано команд:
<b>{teams_count()}</b>

━━━━━━━━━━━━━━

Для регистрации нажмите

📝 <b>Регистрация</b>

⚠️ Можно участвовать только один раз под одним названием команды.
"""

    await update.message.reply_html(
        text,
        reply_markup=main_menu(user.id in ADMIN_IDS)
    )