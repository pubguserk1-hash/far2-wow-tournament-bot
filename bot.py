from telegram.ext import (
    Application,
    CommandHandler,
)

from config import TOKEN
from database import create_database

from handlers.start import start


def main():

    # Создаем базу данных
    create_database()

    # Создаем приложение
    app = Application.builder().token(TOKEN).build()

    # Команда /start
    app.add_handler(CommandHandler("start", start))

    print("====================================")
    print("FAR2 WOW TOURNAMENT BOT ЗАПУЩЕН")
    print("====================================")

    app.run_polling()


if __name__ == "__main__":
    main()