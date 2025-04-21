import discord
from discord.ext import commands
from discord import SlashCommandGroup, option

from anilist.user import get_user_info
from utils.database import get_user_token
from utils.formatters import format_watch_time
from utils.embeds import create_anilist_embed, create_error_embed, ANILIST_COLOR


class ProfileCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    profile = SlashCommandGroup(
        "profile",
        "Commands related to user profiles",
        integration_types={discord.IntegrationType.guild_install},
    )

    @profile.command(
        name="view", description="View your AniList profile or another user's profile"
    )
    @option(
        "user",
        discord.Member,
        description="The user whose profile you want to view",
        required=False,
    )
    async def profile_view(
        self, ctx: discord.ApplicationContext, user: discord.Member = None
    ):
        target_user = user or ctx.author
        user_auth = get_user_token(target_user.id)
        if not user_auth:
            if target_user.id == ctx.author.id:
                error_embed = create_error_embed(
                    "❌ Not Connected",
                    "You haven't connected your AniList account yet. Use `/anilist connect` to connect your account.",
                )
            else:
                error_embed = create_error_embed(
                    "❌ Not Connected",
                    f"{target_user.mention} hasn't connected their AniList account yet.",
                )
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        from anilist.auth import get_valid_token

        access_token = await get_valid_token(target_user.id)

        if not access_token:
            error_embed = create_error_embed(
                "❌ Authentication Error",
                "Failed to get a valid authentication token. Please try reconnecting your AniList account with `/anilist connect`.",
            )
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        await ctx.defer()

        try:
            response = await get_user_info(access_token)
            if "errors" in response:
                error_embed = create_error_embed(
                    "❌ Error",
                    f"Failed to retrieve profile data: {response['errors'][0]['message']}",
                )
                await ctx.followup.send(embed=error_embed)
                return

            user_data = response["data"]["Viewer"]

            embed = discord.Embed(
                title=f"{user_data['name']}'s Profile",
                description=user_data.get("about", "No bio provided."),
                color=ANILIST_COLOR,
            )

            if user_data.get("avatar") and user_data["avatar"].get("large"):
                embed.set_thumbnail(url=user_data["avatar"]["large"])

            if user_data.get("bannerImage"):
                embed.set_image(url=user_data["bannerImage"])

            anime_stats = user_data["statistics"]["anime"]
            manga_stats = user_data["statistics"]["manga"]

            anime_watched = anime_stats["count"]
            episodes_watched = anime_stats["episodesWatched"]
            minutes_watched = anime_stats["minutesWatched"]
            watch_time = format_watch_time(minutes_watched)

            manga_read = manga_stats["count"]
            chapters_read = manga_stats["chaptersRead"]
            volumes_read = manga_stats["volumesRead"]

            embed.add_field(
                name="📺 Anime Stats",
                value=f"Completed: **{anime_watched}**\nEpisodes: **{episodes_watched}**\nWatch time: **{watch_time}**",
                inline=False,
            )

            embed.add_field(
                name="📚 Manga Stats",
                value=f"Completed: **{manga_read}**\nChapters: **{chapters_read}**\nVolumes: **{volumes_read}**",
                inline=False,
            )

            embed.add_field(
                name="🔗 AniList Profile",
                value=f"[View on AniList](https://anilist.co/user/{user_data['name']})",
                inline=False,
            )

            embed.set_footer(
                text=f"Requested by {ctx.author.display_name}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
            )

            await ctx.followup.send(embed=embed)

        except Exception as e:
            error_embed = create_error_embed(
                "❌ Error", f"Failed to retrieve profile data: {str(e)}"
            )
            await ctx.followup.send(embed=error_embed)

    @profile.command(
        name="compare", description="Compare your AniList profile with another user"
    )
    @option(
        "user",
        discord.Member,
        description="The user to compare your profile with",
        required=True,
    )
    async def profile_compare(
        self, ctx: discord.ApplicationContext, user: discord.Member
    ):
        user1_auth = get_user_token(ctx.author.id)
        user2_auth = get_user_token(user.id)

        if not user1_auth:
            error_embed = create_error_embed(
                "❌ Not Connected",
                "You haven't connected your AniList account yet. Use `/anilist connect` to connect your account.",
            )
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        if not user2_auth:
            error_embed = create_error_embed(
                "❌ Not Connected",
                f"{user.mention} hasn't connected their AniList account yet.",
            )
            await ctx.respond(embed=error_embed, ephemeral=True)
            return

        await ctx.defer()

        try:
            user1_response = await get_user_info(user1_auth[0])
            user2_response = await get_user_info(user2_auth[0])

            if "errors" in user1_response or "errors" in user2_response:
                error_embed = create_error_embed(
                    "❌ Error", "Failed to retrieve profile data for one or both users."
                )
                await ctx.followup.send(embed=error_embed)
                return

            user1_data = user1_response["data"]["Viewer"]
            user2_data = user2_response["data"]["Viewer"]

            embed = discord.Embed(
                title="Profile Comparison",
                description=f"Comparing {ctx.author.mention} and {user.mention}",
                color=ANILIST_COLOR,
            )

            embed.add_field(
                name="📺 Anime Stats",
                value=f"**{user1_data['name']}**: {user1_data['statistics']['anime']['count']} anime, {user1_data['statistics']['anime']['episodesWatched']} episodes\n"
                f"**{user2_data['name']}**: {user2_data['statistics']['anime']['count']} anime, {user2_data['statistics']['anime']['episodesWatched']} episodes",
                inline=False,
            )

            embed.add_field(
                name="📚 Manga Stats",
                value=f"**{user1_data['name']}**: {user1_data['statistics']['manga']['count']} manga, {user1_data['statistics']['manga']['chaptersRead']} chapters\n"
                f"**{user2_data['name']}**: {user2_data['statistics']['manga']['count']} manga, {user2_data['statistics']['manga']['chaptersRead']} chapters",
                inline=False,
            )

            await ctx.followup.send(embed=embed)

        except Exception as e:
            error_embed = create_error_embed(
                "❌ Error", f"Failed to compare profiles: {str(e)}"
            )
            await ctx.followup.send(embed=error_embed)


def setup(bot):
    bot.add_cog(ProfileCommands(bot))
