import sqlite3
import os

DB_FOLDER = "database"
DB_PATH = os.path.join(DB_FOLDER, "tournament.db")


def connect():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)

    return sqlite3.connect(DB_PATH)


def create_database():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS teams(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        telegram_id INTEGER UNIQUE,

        username TEXT,

        team_name TEXT UNIQUE,

        player1 TEXT UNIQUE,

        player2 TEXT UNIQUE

    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings(

      key TEXT PRIMARY KEY,

      value TEXT

)
""")

    conn.commit()
    conn.close()


def user_registered(user_id):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM teams WHERE telegram_id=?",
        (user_id,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


def team_exists(team_name):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM teams WHERE LOWER(team_name)=LOWER(?)",
        (team_name,)
    )

    result = cursor.fetchone()

    conn.close()

    return result is not None


def nickname_exists(nickname):

    conn = connect()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id FROM teams
    WHERE
    LOWER(player1)=LOWER(?)
    OR
    LOWER(player2)=LOWER(?)
    """, (nickname, nickname))

    result = cursor.fetchone()

    conn.close()

    return result is not None


def add_team(
        telegram_id,
        username,
        team_name,
        player1,
        player2):

    conn = connect()

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO teams(

    telegram_id,

    username,

    team_name,

    player1,

    player2

    )

    VALUES(?,?,?,?,?)

    """, (

        telegram_id,

        username,

        team_name,

        player1,

        player2

    ))

    conn.commit()

    conn.close()


def get_team(user_id):

    conn = connect()

    cursor = conn.cursor()

    cursor.execute("""

    SELECT

    team_name,

    player1,

    player2,

    username

    FROM teams

    WHERE telegram_id=?

    """, (user_id,))

    result = cursor.fetchone()

    conn.close()

    return result


def get_all_teams():

    conn = connect()

    cursor = conn.cursor()

    cursor.execute("""

    SELECT

    team_name,

    player1,

    player2,

    username

    FROM teams

    ORDER BY id

    """)

    result = cursor.fetchall()

    conn.close()

    return result


def teams_count():

    conn = connect()

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM teams")

    count = cursor.fetchone()[0]

    conn.close()

    return count


def delete_team(user_id):

    conn = connect()

    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM teams WHERE telegram_id=?",
        (user_id,)
    )

    conn.commit()

    conn.close()