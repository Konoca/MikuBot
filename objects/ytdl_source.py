import discord
from discord.ext import commands
import yt_dlp
import asyncio

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(id)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    # 'verbose': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',  # bind to ipv4 since ipv6 addresses cause issues sometimes
    # 'cookiefile': 'cookies.txt',
}

ffmpeg_options = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)


class YTVid:
    def __init__(self, result: dict, timestamp: int = 0):
        self.id: str = result.get('id')
        self.title: str = result.get('title')
        self.duration: str = result.get('duration')
        self.thumbnail: str = result.get('thumbnail')
        self.channel: str = result.get('channel')
        self.original_url: str = result.get('original_url')
        self.url: str = result.get('url')

        self.result = result
        self.timestamp = timestamp

    @classmethod
    def search(cls, search: str, limit: int=5):
        vids = ytdl.extract_info(f'ytsearch{limit}:{search}', download=False)['entries']
        return [cls(vid) for vid in vids]

    @classmethod
    def from_url(cls, url: str):
        vid = ytdl.extract_info(url, download=False)
        return cls(vid)


class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')
        print('Inside of init of YTDLSource')

    @classmethod
    async def from_ytvid(cls, video: YTVid, *, loop=None, timestamp=0):
        loop = loop or asyncio.get_running_loop()
        data = video.result
        print('Data: data')
        ffmpeg_options['options'] = f'-vn -ss {timestamp}'
        return cls(discord.FFmpegPCMAudio(video.url, **ffmpeg_options), data=data)
