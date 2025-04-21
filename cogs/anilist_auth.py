import discord
from discord.ext import commands
from discord import SlashCommandGroup

from anilist.user import get_user_info

from utils.database import is_connected, delete_user_connection, save_user_token

from anilist.auth import get_anilist_oauth_url, exchange_code_for_token, get_valid_token

from utils.embeds import create_anilist_embed, create_error_embed, create_success_embed
from utils.embeds import create_connect_instructions_embed, create_reconnect_embed


class AnilistUtils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.anilist_color = 0x02A9FF

    anilist = SlashCommandGroup("anilist", "AniList Related Commands")

    @anilist.command(
        name="connect", description="Connect your AniList account to the bot"
    )
    async def connect_anilist(self, ctx):
        if is_connected(ctx.author.id):
            embed = create_anilist_embed(
                "🔄 Account Already Connected",
                "You Already Have An Anilist Account Connected.\nDo You Want To Reconnect With A Different Account ?",
            )
            embed.set_footer(
                text="Use /anilist disconnect To Remove The Current Connection",
            )

            await ctx.respond(embed=embed, view=ReconnectView())
            return

        oauth_url = await get_anilist_oauth_url()
        embed = create_connect_instructions_embed(oauth_url)
        await ctx.respond(embed=embed, view=CodeButton())

    @anilist.command(name="disconnect", description="Disconnect your AniList account")
    async def disconnect_anilist(self, ctx):
        if not is_connected(ctx.author.id):
            embed = create_error_embed(
                "❌ Not Connected", "You Don't Have An Anilist Account Connected."
            )
            await ctx.respond(embed=embed)
            return

        delete_user_connection(ctx.author.id)

        embed = create_success_embed(
            "✅ Account Disconnected",
            "Your AniList Account Has Been Successfully Disconnected.",
        )
        embed.set_footer(text="You Can Reconnect Anytime Using `/anilist connect`")

        await ctx.respond(embed=embed)


class ReconnectView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.button(
        label="Disconnect & Reconnect", style=discord.ButtonStyle.secondary, emoji="🔄"
    )
    async def reconnect_callback(self, button, interaction):
        delete_user_connection(interaction.user.id)
        oauth_url = await get_anilist_oauth_url()
        embed = create_reconnect_embed(oauth_url)
        await interaction.response.edit_message(embed=embed, view=CodeButton())


class CodeButton(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=600)

    @discord.ui.button(
        label="Enter Connection Code", style=discord.ButtonStyle.secondary, emoji="🔑"
    )
    async def button_callback(self, button, interaction):
        await interaction.response.send_modal(CodeModal(title="AniList Connection"))


class CodeModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(
            discord.ui.InputText(
                label="Paste Your AniList Code",
                placeholder="The Code Looks Like : def50200 ...",
                style=discord.InputTextStyle.long,
                required=True,
            )
        )

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            code = self.children[0].value
            token_data = await exchange_code_for_token(code)

            print(code)
            print(token_data)

            if "error" in token_data:
                error_message = token_data.get("error_description", token_data["error"])
                embed = create_error_embed(
                    "❌ Connection Failed",
                    f"Error Connecting to AniList: {error_message}\nPlease Contact the Bot Administrator.",
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            access_token = token_data["access_token"]
            refresh_token = token_data.get("refresh_token", "")
            expires_in = token_data.get("expires_in", 3600)

            user_info = await get_user_info(access_token)

            if "errors" in user_info:
                error_msg = (
                    user_info["errors"][0]["message"]
                    if user_info["errors"]
                    else "Unknown error"
                )
                embed = create_error_embed(
                    "❌ Authentication Error",
                    f"Error Retrieving Your Anilist Profile: {error_msg}",
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return

            anilist_id = user_info["data"]["Viewer"]["id"]
            anilist_name = user_info["data"]["Viewer"]["name"]
            avatar_url = user_info["data"]["Viewer"]["avatar"]["large"]

            save_user_token(
                str(interaction.user.id),
                anilist_id,
                access_token,
                refresh_token,
                expires_in,
            )

            embed = create_success_embed(
                "✅ Connection Successful!",
                f"Your AniList Account **{anilist_name}** Has Been Successfully Connected!",
            )

            if avatar_url:
                embed.set_thumbnail(url=avatar_url)

            embed.add_field(
                name="Available Commands",
                value="• `/anilist profile` - View your AniList profile\n"
                "• `/anilist disconnect` - Disconnect your account",
                inline=False,
            )

            await interaction.followup.send(embed=embed)

        except Exception as e:
            import traceback

            error_details = traceback.format_exc()

            embed = create_error_embed(
                "❌ Error Processing Code",
                f"An Error Occurred While Processing Anilist Code: ```{str(e)}```",
            )
            embed.add_field(
                name="What To Do?",
                value="Please Try Connecting Again Or Contact The Bot Administrator.",
            )

            print(f"AniList Connection Error: {error_details}")

            await interaction.followup.send(embed=embed, ephemeral=True)


class AniListErrorView(discord.ui.View):
    def __init__(self, oauth_url):
        super().__init__(timeout=300)
        self.add_item(
            discord.ui.Button(
                label="Try Again", url=oauth_url, style=discord.ButtonStyle.link
            )
        )


def setup(bot: commands.Bot):
    bot.add_cog(AnilistUtils(bot))
