import discord

ANILIST_COLOR = 0x02A9FF


def create_error_embed(title, description):
    embed = discord.Embed(
        title=title, description=description, color=discord.Color.red()
    )
    return embed


def create_success_embed(title, description):
    embed = discord.Embed(
        title=title, description=description, color=discord.Color.green()
    )
    return embed


def create_warning_embed(title, description):
    embed = discord.Embed(
        title=title, description=description, color=discord.Color.gold()
    )
    return embed


def create_anilist_embed(title, description=None):
    embed = discord.Embed(title=title, description=description, color=ANILIST_COLOR)
    embed.set_thumbnail(url="https://anilist.co/img/icons/icon.svg")
    return embed


def create_connect_instructions_embed(oauth_url):
    embed = create_anilist_embed(
        "🔗 Connect Your AniList Account",
        "Follow These Steps To Connect Your AniList Account :",
    )

    embed.add_field(
        name="Step 1",
        value=f"[Click Here To Authorize]({oauth_url}) The Bot On AniList",
        inline=False,
    )
    embed.add_field(
        name="Step 2",
        value="After Authorizing, Copy The Code From The URL",
        inline=False,
    )
    embed.add_field(
        name="Step 3",
        value="Click The Button Below And Paste The Code",
        inline=False,
    )

    return embed


def create_reconnect_embed(oauth_url):
    embed = create_anilist_embed(
        "🔗 Reconnect Your AniList Account",
        "Your Previous Connection Has Been Removed.\nFollow These Steps To Reconnect:",
    )

    embed.add_field(
        name="Step 1",
        value=f"[Click Here To Authorize]({oauth_url}) The Bot On AniList",
        inline=False,
    )
    embed.add_field(
        name="Step 2",
        value="After Authorizing, Copy The Code From The URL",
        inline=False,
    )
    embed.add_field(
        name="Step 3",
        value="Click The Button Below And Paste The Code",
        inline=False,
    )

    return embed
