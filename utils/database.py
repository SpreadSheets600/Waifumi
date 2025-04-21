import time
import sqlite3

DB_PATH = "WaifumiUsers.db"


def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        discord_id TEXT PRIMARY KEY,
        anilist_id TEXT NOT NULL,
        access_token TEXT NOT NULL,
        refresh_token TEXT,
        token_expires_at INTEGER
    )
    """
    )

    conn.commit()
    conn.close()


def save_user_token(discord_id, anilist_id, access_token, refresh_token, expires_in):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    expires_at = int(time.time()) + expires_in

    cursor.execute(
        "INSERT OR REPLACE INTO users (discord_id, anilist_id, access_token, refresh_token, token_expires_at) VALUES (?, ?, ?, ?, ?)",
        (str(discord_id), str(anilist_id), access_token, refresh_token, expires_at),
    )

    conn.commit()
    conn.close()


def get_user_token(discord_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT access_token, refresh_token, token_expires_at FROM users WHERE discord_id = ?",
        (str(discord_id),),
    )
    result = cursor.fetchone()

    conn.close()

    if result:
        return {
            "access_token": result[0],
            "refresh_token": result[1],
            "expires_at": result[2],
        }
    return None


def get_anilist_id(discord_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT anilist_id FROM users WHERE discord_id = ?", (str(discord_id),)
    )
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    return None


def is_connected(discord_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE discord_id = ?", (str(discord_id),)
    )
    count = cursor.fetchone()[0]

    conn.close()
    return count > 0


def delete_user_connection(discord_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users WHERE discord_id = ?", (str(discord_id),))
    conn.commit()
    conn.close()
