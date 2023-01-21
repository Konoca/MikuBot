import discord
from discord.ext import commands
from objects import EmbedMaker

class Main(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    """ Events """
    @commands.Cog.listener()
    async def on_ready(self):
        print('Syncing...')
        await self.bot.tree.sync()
        print(f'{self.bot.user.name}#{self.bot.user.discriminator} online')


async def setup(bot):
    await bot.add_cog(Main(bot))
