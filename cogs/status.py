from typing import List
import discord
from discord.ext import commands
from discord import app_commands
import json
from objects import PermissionDecorators

class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file = './data/profile.json'

    """ Events """
    @commands.Cog.listener()
    async def on_ready(self):
        await self.startup_status()
        print('Status cog ready!')

    """ Helpers """

    def parse_type(self, type: str):
        match type:
            case 'playing':
                return "Playing", discord.ActivityType.playing
            case 'listening':
                return "Listening to", discord.ActivityType.listening
            case 'watching':
                return "Watching", discord.ActivityType.watching
            case _:
                return None

    async def startup_status(self):
        with open(self.file, 'r') as f:
            status = json.load(f).get('status')

        if not status:
            return

        activity_type_str, activity_type = self.parse_type(status.get('type'))
        activity_name = status.get('name')

        activity = discord.Activity(
            type=activity_type,
            name=activity_name
        )

        if activity_type:
            await self.bot.change_presence(activity=activity)
            return f'{activity_type_str} {activity_name}'
        return 'Nothing'

    async def set_activity(self, user, activity_type, activity_name):
        with open(self.file, 'r') as f:
            data = json.load(f)

        data.get('status_history', []).append(data.get('status', {}))

        status = {
            'type': activity_type,
            'name': activity_name,
            'user': user
        }

        data['status'] = status

        with open(self.file, 'w') as f:
            f.write(json.dumps(data, indent=4))

        return await self.startup_status()

    """ Commands """

    @PermissionDecorators.is_bot_mod
    @app_commands.command(name='status', description='Set bot status')
    @app_commands.choices(activity_type=[
        app_commands.Choice(name='playing', value='playing'),
        app_commands.Choice(name='listening to', value='listening'),
        app_commands.Choice(name='watching', value='watching')
    ])
    async def change_status(self, interaction: discord.Interaction, activity_type: app_commands.Choice[str], activity_name: str):
        try:
            user = f'{interaction.user.name}#{interaction.user.discriminator} ({interaction.user.id})'
            status = await self.set_activity(user, activity_type.value, activity_name)
            await interaction.response.send_message(f'Set status to: {status}')
            print(f'{user} set status to {status}')
        except Exception as e:
            print(e)


async def setup(bot):
    await bot.add_cog(Status(bot))
