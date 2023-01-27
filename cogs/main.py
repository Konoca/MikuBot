import discord
from discord.ext import commands
from discord import app_commands
import json
from objects import EmbedMaker

class Main(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    """ Events """

    @commands.Cog.listener()
    async def on_ready(self):
        print('Syncing...')
        await self.bot.tree.sync()
        print(f'{self.bot.user.name}#{self.bot.user.discriminator} online in {len(self.bot.guilds)} servers')

    """ Commands """

    @app_commands.command(name='changelogs', description='Display changes made to bot')
    async def changelogs(self, interaction: discord.Interaction):
        with open('./data/changelogs.json', 'r') as f:
            data = json.load(f)

        changes = data['current']
        embed = EmbedMaker(title='Changelogs')
        for index, change in enumerate(changes):
            embed.add_field(name=f'{index+1}) {change}')
        await embed.send_embed(interaction, response=True)


async def setup(bot):
    await bot.add_cog(Main(bot))
