import os
import sqlite3
import aiohttp
from json import load
from dotenv import load_dotenv

load_dotenv()

ANILIST_CLIENT_ID = "26192"
ANILIST_REDIRECT_URI = "https://anilist.co/api/v2/oauth/pin"
ANILIST_CLIENT_SECRET = "AOOUPs6Jtz2kJ8bdqprNIrYJK2izGaJIUaRrrX3f"


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
            bannerImage
            about
            statistics {
                anime {
                    count
                    minutesWatched
                    episodesWatched
                    genres {
                        genre
                        count
                    }
                }
                manga {
                    count
                    chaptersRead
                    volumesRead
                    genres {
                        genre
                        count
                    }
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


async def refresh_access_token(refresh_token):
    url = "https://anilist.co/api/v2/oauth/token"
    data = {
        "grant_type": "refresh_token",
        "client_id": ANILIST_CLIENT_ID,
        "client_secret": ANILIST_CLIENT_SECRET,
        "refresh_token": refresh_token,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data) as response:
            return await response.json()


async def get_valid_token(discord_id):

    import time

    token_data = get_user_token(discord_id)
    if not token_data:
        return None

    current_time = int(time.time())

    if token_data["expires_at"] > current_time + 300:
        return token_data["access_token"]

    if token_data["refresh_token"]:
        new_token_data = await refresh_access_token(token_data["refresh_token"])

        if "access_token" in new_token_data:

            user_info = await get_anilist_user_info(new_token_data["access_token"])
            anilist_id = user_info["data"]["Viewer"]["id"]

            save_user_token(
                discord_id,
                anilist_id,
                new_token_data["access_token"],
                new_token_data.get("refresh_token", token_data["refresh_token"]),
                new_token_data.get("expires_in", 3600),
            )

            return new_token_data["access_token"]

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


def is_connected(discord_id):
    conn = sqlite3.connect("WaifumiUsers.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM users WHERE discord_id = ?", (str(discord_id),)
    )
    count = cursor.fetchone()[0]

    conn.close()
    return count > 0
