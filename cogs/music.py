import discord
from discord.ext import commands
from discord import app_commands
import asyncio
from objects import YTDLSource, YTVid, EmbedMaker, GuildData
import traceback

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.guilds: dict[int, GuildData] = {}

    """Events"""

    @commands.Cog.listener()
    async def on_ready(self):
        print('Music cog ready!')

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceChannel):
        guild = self.guilds[member.guild.id]
        if len(guild.voice_client.channel.members) == 1:
            await guild.voice_client.disconnect()
            guild.voice_client = None
            guild.current_video = None
            await self.end_task(guild)
            guild.song_queue = []

    """Helpers"""

    def end_video(self, yt_vid: YTVid, guild: GuildData):
        print(f'[{guild.id}] Ended: {yt_vid.title}')
        guild.current_video = None
        if guild.repeat_video:
            return
        guild.song_queue.remove(yt_vid)

    async def start_playing(self, interaction: discord.Interaction):
        guild = self.guilds[interaction.guild_id]

        while len(guild.song_queue) > 0 and guild.current_video and guild.voice_client:
            source: YTDLSource = await YTDLSource.from_ytvid(guild.current_video, loop=self.bot.loop, timestamp=guild.current_video.timestamp)
            guild.voice_client.play(source, after=lambda e: print(f'Player error: {e}') if e else None)
            guild.current_video.timestamp = 0

            print(f'[{guild.id}] Started: {guild.current_video.title}')

            if not guild.repeat_video:
                embed = EmbedMaker(title=f'Now playing: {guild.current_video.title}', description=f'By: {guild.current_video.channel}')
                embed.add_thumbnail(guild.current_video)
                await embed.send_embed(interaction)

            while guild.current_video and (guild.voice_client.is_playing() or guild.voice_client.is_paused()):
                await asyncio.sleep(2)

            self.end_video(guild.current_video, guild)

            if not guild.song_queue == []:
                guild.current_video = guild.song_queue[0]

        await self.end_task(guild)

    async def end_task(self, guild: GuildData):
        if not guild.music_task:
            return

        guild.music_task.cancel()
        try:
            await guild.music_task
        except asyncio.CancelledError:
            guild.music_task = None

    def is_in_voice_channel(self, interaction: discord.Interaction):
        return self.guilds.get(interaction.guild_id) and self.guilds[interaction.guild_id].voice_client

    """Commands"""

    @app_commands.command(name='play', description='Play a youtube video (specifying timestamp may delay audio)')
    async def play(self, interaction: discord.Interaction, query_or_url: str, timestamp_in_seconds: int = 0):
        if not interaction.user.voice:
            await EmbedMaker.error_response(interaction, 'You are not connected to a voice channel')
            return

        if not self.guilds.get(interaction.guild_id):
            self.guilds[interaction.guild_id] = GuildData(interaction.guild_id)

        guild = self.guilds[interaction.guild_id]

        if not guild.voice_client:
            channel = interaction.user.voice.channel
            voice_client = await channel.connect(timeout=120.0)
            guild.voice_client = voice_client
            guild.repeat_video = False

        if not query_or_url.startswith('https://'):
            await interaction.response.defer(thinking=True)
            search_results = YTVid.search(query_or_url)
            yt_vid: YTVid = await EmbedMaker.create_yt_search_embed(interaction, self.bot, query_or_url, search_results)
            if not yt_vid:
                return
        else:
            yt_vid: YTVid = YTVid.from_url(query_or_url)
            await EmbedMaker.create_text_embed(interaction, 'Found video', yt_vid.title, response=True)

        yt_vid.timestamp = timestamp_in_seconds
        guild.song_queue.append(yt_vid)

        if len(guild.song_queue) == 1 and not guild.current_video:
            guild.current_video = yt_vid
            # await interaction.channel.send(f'**Selected:** {yt_vid.title}')
            guild.music_task = asyncio.create_task(self.start_playing(interaction))
        else:
            await interaction.channel.send(f"**Queued at position {len(guild.song_queue) - 1}:** {yt_vid.title}")

    @app_commands.command(name='leave', description='Remove bot from voice channel')
    async def leave(self, interaction: discord.Interaction):
        if not self.is_in_voice_channel(interaction):
            return

        guild = self.guilds[interaction.guild_id]

        await interaction.response.send_message('Leaving voice channel')
        await guild.voice_client.disconnect()

        guild.voice_client = None
        guild.current_video = None
        await self.end_task(guild)
        guild.song_queue = []

    @app_commands.command(name='pause', description='Pause player')
    async def pause(self, interaction: discord.Interaction):
        if not self.is_in_voice_channel(interaction):
            return

        guild = self.guilds[interaction.guild_id]

        if guild.voice_client.is_playing():
            await interaction.response.send_message('Player paused')
            guild.voice_client.pause()

    @app_commands.command(name='resume', description='Resume player')
    async def resume(self, interaction: discord.Interaction):
        if not self.is_in_voice_channel(interaction):
            return
        guild = self.guilds[interaction.guild_id]

        if guild.voice_client.is_paused():
            await interaction.response.send_message('Player resumed')
            guild.voice_client.resume()

    @app_commands.command(name='stop', description='Stops player')
    async def stop(self, interaction: discord.Interaction):
        if not self.is_in_voice_channel(interaction):
            return

        guild = self.guilds[interaction.guild_id]

        guild.voice_client.stop()

        await interaction.response.send_message('Player stopped')

        if guild.current_video:
            self.end_video(guild.current_video, guild)

        await self.end_task(guild)
        guild.song_queue = []

    @app_commands.command(name='skip', description='Skip current audio track')
    async def skip(self, interaction: discord.Interaction):
        if not self.is_in_voice_channel(interaction):
            return

        guild = self.guilds[interaction.guild_id]

        if not guild.current_video:
            await EmbedMaker.error_response(interaction, 'Nothing is currently playing')
            return

        await EmbedMaker.create_text_embed(interaction, 'Skipping', f'{guild.current_video.title}', response=True)
        guild.voice_client.stop()

    @app_commands.command(name='queue', description='Show queue')
    async def queue(self, interaction: discord.Interaction):
        if not self.is_in_voice_channel(interaction):
            return

        guild = self.guilds[interaction.guild_id]

        embed = EmbedMaker('Queue', '') if guild.song_queue else EmbedMaker('Queue', '**Queue empty**')

        for index, video in enumerate(guild.song_queue):
            idx = f'{index})' if index != 0 else 'Currently playing:'
            embed.add_field(name=f'{idx} {video.title}', value=f'By: {video.channel}')

        await embed.send_embed(interaction, response=True)

    @app_commands.command(name='repeat', description='Repeat current song')
    @app_commands.choices(toggle=[
        app_commands.Choice(name='on', value=1),
        app_commands.Choice(name='off', value=0)
    ])
    async def repeat(self, interaction: discord.Interaction, toggle: app_commands.Choice[int]):
        if not self.is_in_voice_channel(interaction):
            return

        guild = self.guilds[interaction.guild_id]

        guild.repeat_video = False
        if toggle.value:
            guild.repeat_video = True

        await interaction.response.send_message(f'Repeating of {guild.current_video.title} set to {guild.repeat_video}')

    @app_commands.command(name='seek', description='Change current position in song')
    async def seek(self, interaction: discord.Interaction, timestamp_in_seconds: int):
        if not self.is_in_voice_channel(interaction):
            return

        guild = self.guilds[interaction.guild_id]

        if not guild.voice_client.is_playing():
            await EmbedMaker.error_response(interaction, 'Nothing is currently playing')
            return

        guild.current_video.timestamp = timestamp_in_seconds
        currentRepeat = guild.repeat_video
        guild.repeat_video = True
        guild.voice_client.stop()
        await EmbedMaker.create_text_embed(interaction, 'Current Timestamp(in seconds)', f'Setting to {timestamp_in_seconds}', response=True) # had to be put here so that it would actually send the msg as a response

        while not guild.voice_client.is_playing():
            await asyncio.sleep(1)
        guild.repeat_video = currentRepeat


async def setup(bot):
    await bot.add_cog(Music(bot))
