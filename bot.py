import os
import discord
import sqlite3
import datetime
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()

DISCORD_TOKEN = ()


intents = discord.Intents.all()

bot = commands.Bot(intents=intents)
bot.remove_command("help")


def setup_database():
    conn = sqlite3.connect("WaifumiUsers.db")
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS users (
        discord_id TEXT PRIMARY KEY,
        anilist_id TEXT,
        access_token TEXT,
        refresh_token TEXT,
        token_expires_at INTEGER
    )
    """
    )

    conn.commit()
    conn.close()


@bot.event
async def on_ready():
    print("--------------------------------")
    print("Waifumi Bot Is Online")
    print("--------------------------------")
    print(f"{bot.user.name} ( {bot.user.id} )")
    print("----- + LOADING COMMANDS + -----")
    print("--------------------------------")

    start_time = datetime.datetime.now()
    bot.start_time = start_time

    commands = 0

    for command in bot.walk_application_commands():
        commands += 1

        print(f"----- + Loaded : {command.name} ")

    print("--------------------------------")
    print(f"---- + Loaded : {commands}  Commands + -")
    print("--------------------------------")

    print("------- + LOADING COGS + -------")
    print(f"----- + Loaded : {len(bot.cogs)} Cogs + ------")
    print("--------------------------------")

    setup_database()


@bot.slash_command(
    name="ping",
    description="Check Bot's Latency & Uptime",
    integration_types={
        discord.IntegrationType.guild_install,
    },
)
async def ping(ctx: discord.ApplicationContext):
    latency = bot.latency * 1000
    uptime = datetime.datetime.now() - bot.start_time

    uptime_seconds = uptime.total_seconds()
    uptime_str = str(datetime.timedelta(seconds=uptime_seconds)).split(".")[0]

    embed = discord.Embed(
        title=":ping_pong: _*Pong !*_",
        description=f"Uptime : {uptime_str}\nLatency : {latency:.2f} ms",
        color=0x2F3136,
    )

    await ctx.respond(embed=embed)


@bot.slash_command(
    name="info",
    description="Get Bot Information",
    integration_types={
        discord.IntegrationType.guild_install,
    },
)
async def info(ctx: discord.ApplicationContext):
    embed = discord.Embed(
        title=":information_source: Application Info",
        description="Anilist Discord Bot",
        color=0x2F3136,
    )

    embed.add_field(
        name="Developer",
        value=":gear: `SpreadSheets600`",
        inline=False,
    )

    embed.add_field(
        name="Created At",
        value=f":calendar: `{bot.user.created_at.strftime('%Y-%m-%d %H:%M:%S')}`",
        inline=True,
    )

    try:
        embed.set_thumbnail(url=bot.user.avatar.url)
    except Exception as e:
        print(f"Error Setting Thumbnail: {e}")

    await ctx.respond(embed=embed)


@bot.event
async def on_slash_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandOnCooldown):
        await ctx.respond(
            f":stopwatch: This Command Is On Cooldown. Try Again In {error.retry_after:.2f} Seconds"
        )
    elif isinstance(error, commands.errors.MissingRequiredArgument):
        await ctx.respond(":x: You Are Missing Required Arguments")
    elif isinstance(error, commands.errors.BadArgument):
        await ctx.respond(":x: Bad Argument Provided")
    elif isinstance(error, commands.errors.CommandInvokeError):
        await ctx.respond(":x: An Error Occurred While Executing The Command")
    elif isinstance(error, commands.errors.CommandNotFound):
        await ctx.respond(":x: Command Not Found")
    elif isinstance(error, commands.errors.CheckFailure):
        await ctx.respond(":x: You Do Not Have Permission To Use This Command")
    else:
        await ctx.respond(":x: An Error Occurred")


try:
    bot.load_extension("anilist.utils")
except Exception as e:
    print(f"Error Loading Extension : {e}")

if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables")
    else:
        bot.run(DISCORD_TOKEN)
