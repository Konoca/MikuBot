import asyncio
import discord
from objects import YTVid

class GuildData:
    def __init__(self, id: int):
        self.id: int = id
        self.voice_client: discord.VoiceClient = None
        self.song_queue: list[YTVid] = []
        self.current_video: YTVid = None
        self.repeat_video = False
        self.music_task: asyncio.Task = None

