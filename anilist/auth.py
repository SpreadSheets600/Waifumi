import aiohttp
import time
from config.config import ANILIST_CLIENT_ID, ANILIST_CLIENT_SECRET, ANILIST_REDIRECT_URI
from utils.database import get_user_token, save_user_token


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
    token_data = get_user_token(discord_id)
    if not token_data:
        return None

    current_time = int(time.time())

    if token_data["expires_at"] > current_time + 300:
        return token_data["access_token"]

    if token_data["refresh_token"]:
        new_token_data = await refresh_access_token(token_data["refresh_token"])

        if "access_token" in new_token_data:
            from anilist.user import get_user_info

            user_info = await get_user_info(new_token_data["access_token"])
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
