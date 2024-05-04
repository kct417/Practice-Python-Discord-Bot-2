import random
from typing import Union
import discord
from discord import app_commands
from dotenv import dotenv_values

MY_GUILD = discord.Object(dotenv_values(".env")["GUILD_ID"])


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


def run_bot():
    intents = discord.Intents.all()

    client = MyClient(intents=intents)

    @client.event
    async def on_ready():
        print(client.user)

    @client.tree.command(name="channel-info")
    @app_commands.describe(channel="Channel to get info of")
    async def channel_info(
        interaction: discord.Interaction,
        channel: Union[discord.VoiceChannel, discord.TextChannel],
    ):
        embed = discord.Embed(title="Channel Info")
        embed.add_field(name="Name", value=channel.name, inline=True)
        embed.add_field(name="ID", value=channel.id, inline=True)
        embed.add_field(
            name="Type",
            value="Voice" if isinstance(channel, discord.VoiceChannel) else "Text",
            inline=True,
        )

        embed.set_footer(text="Created").timestamp = channel.created_at
        await interaction.response.send_message(embed=embed)

    @client.tree.command(name="roll")
    @app_commands.describe(upper="Upper bound", lower="Lower bound")
    async def roll(interaction: discord.Interaction, upper: int = 6, lower: int = 1):
        if upper < lower:
            await interaction.response.send_message(
                "Upper bound must be greater than lower bound"
            )
            return
        await interaction.response.send_message(random.randint(lower, upper))

    @client.tree.context_menu(name="Report to Server Moderators")
    async def report_message(
        interaction: discord.Interaction, message: discord.Message
    ):
        await interaction.response.send_message(
            f"Thanks for reporting this message by {message.author.mention} to our moderators.",
            ephemeral=True,
        )

        embed = discord.Embed(title="Reported Message")
        if message.content:
            embed.description = message.content

        embed.set_author(
            name=message.author.display_name, icon_url=message.author.display_avatar.url
        )
        embed.timestamp = message.created_at

        url_view = discord.ui.View()
        url_view.add_item(
            discord.ui.Button(
                label="Go to Message",
                style=discord.ButtonStyle.url,
                url=message.jump_url,
            )
        )

        if interaction.guild:
            log_channel = interaction.guild.get_channel(
                int(dotenv_values(".env")["LOGGING_ID"])
            )
            await log_channel.send(embed=embed, view=url_view)

    client.run(dotenv_values(".env")["TOKEN"])
