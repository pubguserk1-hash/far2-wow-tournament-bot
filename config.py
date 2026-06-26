import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = [
    int(x)
    for x in os.getenv("ADMIN_IDS").split(",")
]

TOURNAMENT_NAME = "🏆 FAR2 WOW TOURNAMENT"

PRIZE = "5000 UC"

RULES = """
📖 Правила турнира

• Формат 2x2 WOW
• Один игрок может участвовать только в одной команде
• Одно название команды
• Соблюдать честную игру
"""

INFO = """
ℹ️ Информация

🎁 Приз:
5000 UC

🎮 PUBG MOBILE WOW

👤 Организатор:
@ТВОЙ_USERNAME
"""