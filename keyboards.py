from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# Главное меню
def main_menu(is_admin=False):

    keyboard = [
        [
            InlineKeyboardButton(
                "📝 Регистрация",
                callback_data="register"
            )
        ],
        [
            InlineKeyboardButton(
                "👥 Моя команда",
                callback_data="my_team"
            )
        ],
        [
            InlineKeyboardButton(
                "📖 Правила",
                callback_data="rules"
            )
        ]
    ]

    if is_admin:
        keyboard.append(
            [
                InlineKeyboardButton(
                    "👑 Админ-панель",
                    callback_data="admin_panel"
                )
            ]
        )

    return InlineKeyboardMarkup(keyboard)


# Подтверждение регистрации
def confirm_registration():

    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Подтвердить",
                callback_data="confirm_register"
            ),
            InlineKeyboardButton(
                "❌ Отмена",
                callback_data="cancel_register"
            )
        ]
    ]

    return InlineKeyboardMarkup(keyboard)


# Админ меню
def admin_menu():

    keyboard = [

        [
            InlineKeyboardButton(
                "📋 Все команды",
                callback_data="all_teams"
            )
        ],

        [
            InlineKeyboardButton(
                "📊 Статистика",
                callback_data="stats"
            )
        ],

        [
            InlineKeyboardButton(
                "📤 Excel",
                callback_data="excel"
            )
        ],

        [
            InlineKeyboardButton(
                "📢 Рассылка",
                callback_data="broadcast"
            )
        ],

        [
            InlineKeyboardButton(
                "🔍 Поиск команды",
                callback_data="search"
            )
        ],

        [
            InlineKeyboardButton(
                "🗑 Удалить команду",
                callback_data="delete_team"
            )
        ],

        [
            InlineKeyboardButton(
                "⬅ Назад",
                callback_data="back"
            )
        ]

    ]

    return InlineKeyboardMarkup(keyboard)