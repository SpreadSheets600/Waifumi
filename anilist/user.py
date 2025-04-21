import aiohttp


async def get_user_info(access_token):
    """Get user information from AniList API"""
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


async def execute_anilist_query(query, variables=None, access_token=None):
    url = "https://graphql.anilist.co"

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"

    json_data = {"query": query}
    if variables:
        json_data["variables"] = variables

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=json_data, headers=headers) as response:
            return await response.json()
