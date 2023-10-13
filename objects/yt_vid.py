from youtubesearchpython.__future__ import VideosSearch
from youtubesearchpython import Video

class YTVid:
    def __init__(self, result: dict):
        self.type: str = result.get('type')
        self.id: str = result.get('id')
        self.title: str = result.get('title')
        self.published_time: str = result.get('publishedTime')
        self.duration: str = result.get('duration')
        self.view_count: ViewCount = ViewCount(result.get('viewCount'))
        thumbnails = result.get('thumbnails')
        self.thumbnails: list[Thumbnail] = [Thumbnail(thumbnail) for thumbnail in thumbnails] if thumbnails else []
        self.rich_thumbnail: Thumbnail = Thumbnail(result.get('richThumbnail'))
        snippets = result.get('descriptionSnippet')
        self.description_snippet: list[DescriptionSnippet] = [DescriptionSnippet(snippet) for snippet in snippets] if snippets else []
        self.channel: Channel = Channel(result.get('channel'))
        self.accessibility: Accessibility = Accessibility(result.get('accessibility'))
        self.link: str = result.get('link')
        self.shelf_title = result.get('shelfTitle')

    @classmethod
    async def search(cls, search: str, limit: int=5):
        vids = VideosSearch(search, limit=limit)
        vids = await vids.next()
        return [YTVid(vid) for vid in vids['result']]

    @classmethod
    def from_url(cls, url: str):
        return cls(Video.getInfo(url))

class ViewCount:
    def __init__(self, view_count: dict):
        self.text: str = view_count.get('text') if view_count else ''
        self.short: str = view_count.get('short') if view_count else ''


class Thumbnail:
    def __init__(self, thumbnail: dict):
        self.url: str = thumbnail.get('url') if thumbnail else ''
        self.width: int = thumbnail.get('width') if thumbnail else 0
        self.height: int = thumbnail.get('height') if thumbnail else 0


class DescriptionSnippet:
    def __init__(self, snippet: dict):
        self.text: str = snippet.get('text') if snippet else ''
        self.bold: bool = snippet.get('bold', False) if snippet else False


class Channel:
    def __init__(self, channel: dict):
        self.name: str = channel.get('name') if channel else ''
        self.id: str  = channel.get('id') if channel else ''
        thumbnails = channel.get('thumbnails')
        self.thumbnails: list[Thumbnail] = [Thumbnail(thumbnail) for thumbnail in thumbnails] if thumbnails else []
        self.link: str = channel.get('link') if channel else ''


class Accessibility:
    def __init__(self, access: dict):
        self.title: str = access.get('title') if access else ''
        self.duration: str = access.get('duration') if access else ''
