from discord.ext import commands

from anilist.auth import get_valid_token
from anilist.user import get_user_info


def setup(bot: commands.Bot):
    from cogs.anilist_auth import AnilistUtils
    from cogs.profile_commands import ProfileCommands

    bot.add_cog(AnilistUtils(bot))
    bot.add_cog(ProfileCommands(bot))

    from utils.database import setup_database

    setup_database()
