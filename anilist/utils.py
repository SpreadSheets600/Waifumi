import discord
from discord.ext import commands
from discord import SlashCommandGroup

from .connect import *


class AnilistUtils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    anilist = SlashCommandGroup("anilist", "AniList Related Commands")

    @anilist.command(name="connect", description="Connect Your AniList Account")
    async def connect_anilist(self, ctx):
        oauth_url = await get_anilist_oauth_url()
        embed = discord.Embed(
            title="Connect Your AniList Account",
            description=f"Click the link below to authorize the bot to access your AniList account:\n\n[Connect AniList]({oauth_url})",
            color=0x02A9FF,
        )
        await ctx.send(embed=embed, view=CodeButton())

    @anilist.command(name="disconnect", description="Disconnect Your AniList Account")
    async def disconnect_anilist(self, ctx):
        conn = sqlite3.connect("WaifumiUsers.db")
        cursor = conn.cursor()

        cursor.execute("DELETE FROM users WHERE discord_id = ?", (str(ctx.author.id),))
        conn.commit()
        conn.close()

        await ctx.send("Successfully disconnected your AniList account!")

        await ctx.author.send("Successfully disconnected your AniList account!")


class CodeButton(discord.ui.View):
    @discord.ui.button(label="Set Account Code", style=discord.ButtonStyle.secondary)
    async def button_callback(self, button, interaction):
        await interaction.response.send_modal(
            CodeModal(title="Anilist Account Connection")
        )


class CodeModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(
            discord.ui.InputText(
                label="Input Anilist Code", style=discord.InputTextStyle.long
            )
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            token_data = await exchange_code_for_token(self.children[0].value)

            if "error" in token_data:
                await interaction.response.send_message(
                    f"Error Connecting Your AniList Account : {token_data['error']}"
                )
                return

            access_token = token_data["access_token"]
            refresh_token = token_data.get("refresh_token", "")
            expires_in = token_data.get("expires_in", 3600)

            user_info = await get_anilist_user_info(access_token)
            anilist_id = user_info["data"]["Viewer"]["id"]
            anilist_name = user_info["data"]["Viewer"]["name"]

            save_user_token(
                interaction.response.send_message,
                anilist_id,
                access_token,
                refresh_token,
                expires_in,
            )

            await interaction.response.send_message(
                f"Successfully Connected To Your Anilist Account : {anilist_name}!"
            )
        except Exception as e:
            await interaction.response.send_message(
                f"Error Processing Authorization Code : {str(e)}"
            )


def setup(bot: commands.Bot):
    bot.add_cog(AnilistUtils(bot))
