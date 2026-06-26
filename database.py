import aiosqlite
import os

DB_FOLDER = "database"
DB_PATH = os.path.join(DB_FOLDER, "tournament.db")


async def create_database():

    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS teams(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            telegram_id INTEGER UNIQUE,

            username TEXT,

            team_name TEXT UNIQUE,

            player1 TEXT UNIQUE,

            player2 TEXT UNIQUE,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS settings(

            key TEXT PRIMARY KEY,

            value TEXT

        )
        """)

        await db.execute("""
        INSERT OR IGNORE INTO settings(key,value)

        VALUES('registration','open')
        """)

        await db.commit()


# ---------------------------------------------------


async def registration_open():

    async with aiosqlite.connect(DB_PATH) as db:

        async with db.execute(
            "SELECT value FROM settings WHERE key='registration'"
        ) as cursor:

            result = await cursor.fetchone()

            return result[0] == "open"


# ---------------------------------------------------


async def close_registration():

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""

        UPDATE settings

        SET value='closed'

        WHERE key='registration'

        """)

        await db.commit()


# ---------------------------------------------------


async def open_registration():

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""

        UPDATE settings

        SET value='open'

        WHERE key='registration'

        """)

        await db.commit()


# ---------------------------------------------------


async def user_registered(user_id):

    async with aiosqlite.connect(DB_PATH) as db:

        async with db.execute(
            "SELECT id FROM teams WHERE telegram_id=?",
            (user_id,)
        ) as cursor:

            return await cursor.fetchone()


# ---------------------------------------------------


async def team_exists(team):

    async with aiosqlite.connect(DB_PATH) as db:

        async with db.execute(
            "SELECT id FROM teams WHERE LOWER(team_name)=LOWER(?)",
            (team,)
        ) as cursor:

            return await cursor.fetchone()


# ---------------------------------------------------


async def nickname_exists(name):

    async with aiosqlite.connect(DB_PATH) as db:

        async with db.execute("""

        SELECT id

        FROM teams

        WHERE

        LOWER(player1)=LOWER(?)

        OR

        LOWER(player2)=LOWER(?)

        """, (name, name)) as cursor:

            return await cursor.fetchone()


# ---------------------------------------------------


async def add_team(
        telegram_id,
        username,
        team_name,
        player1,
        player2):

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute("""

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

        await db.commit()


# ---------------------------------------------------


async def get_team(user_id):

    async with aiosqlite.connect(DB_PATH) as db:

        async with db.execute("""

        SELECT

        id,

        team_name,

        player1,

        player2,

        username

        FROM teams

        WHERE telegram_id=?

        """, (user_id,)) as cursor:

            return await cursor.fetchone()


# ---------------------------------------------------


async def get_all_teams():

    async with aiosqlite.connect(DB_PATH) as db:

        async with db.execute("""

        SELECT

        id,

        team_name,

        player1,

        player2,

        username

        FROM teams

        ORDER BY id

        """) as cursor:

            return await cursor.fetchall()


# ---------------------------------------------------


async def delete_team(user_id):

    async with aiosqlite.connect(DB_PATH) as db:

        await db.execute(
            "DELETE FROM teams WHERE telegram_id=?",
            (user_id,)
        )

        await db.commit()


# ---------------------------------------------------


async def teams_count():

    async with aiosqlite.connect(DB_PATH) as db:

        async with db.execute(
            "SELECT COUNT(*) FROM teams"
        ) as cursor:

            result = await cursor.fetchone()

            return result[0]