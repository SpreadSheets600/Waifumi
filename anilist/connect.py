import os
import sqlite3
import aiohttp
from json import load
from dotenv import load_dotenv

load_dotenv()

ANILIST_CLIENT_ID = os.getenv("ANILIST_CLIENT_ID")
ANILIST_CLIENT_SECRET = os.getenv("ANILIST_CLIENT_SECRET")
ANILIST_REDIRECT_URI = os.getenv("ANILIST_REDIRECT_URI")


async def get_anilist_oauth_url():
    return f"https://anilist.co/api/v2/oauth/authorize?client_id={ANILIST_CLIENT_ID}&response_type=code"


async def exchange_code_for_token(code):
    url = "https://anilist.co/api/v2/oauth/token"
    data = {
        "grant_type": "authorization_code",
        "client_id": ANILIST_CLIENT_ID,
        "client_secret": ANILIST_CLIENT_SECRET,
        "redirect_uri": ANILIST_REDIRECT_URI,
        "code": code,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()


async def get_anilist_user_info(access_token):
    query = """
    query {
        Viewer {
            id
            name
            avatar {
                large
            }
            statistics {
                anime {
                    count
                    minutesWatched
                    episodesWatched
                }
            }
        }
    }
    """

    url = "https://graphql.anilist.co"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url, json={"query": query}, headers=headers
        ) as response:
            return await response.json()


def save_user_token(discord_id, anilist_id, access_token, refresh_token, expires_in):
    import time

    conn = sqlite3.connect("WaifumiUsers.db")
    cursor = conn.cursor()

    expires_at = int(time.time()) + expires_in

    cursor.execute(
        "INSERT OR REPLACE INTO users (discord_id, anilist_id, access_token, refresh_token, token_expires_at) VALUES (?, ?, ?, ?, ?)",
        (str(discord_id), str(anilist_id), access_token, refresh_token, expires_at),
    )

    conn.commit()
    conn.close()


def get_user_token(discord_id):
    conn = sqlite3.connect("WaifumiUsers.db")
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
    conn = sqlite3.connect("WaifumiUsers.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT anilist_id FROM users WHERE discord_id = ?", (str(discord_id),)
    )
    result = cursor.fetchone()

    conn.close()

    if result:
        return result[0]
    return None
