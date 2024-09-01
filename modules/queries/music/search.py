from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Union, List, Optional

import json, subprocess, json, urllib.parse
from fuzzywuzzy import process
from modules.core.resources import Resources

class SongVariant:
    __slots__ = ['_kind', '_sequence', '_version']

    def __init__(self, kind: str, sequence: Optional[int] = 1, version: Optional[int] = 1) -> None:
        self._kind = kind
        self._sequence = sequence if sequence and sequence != "None" else 1
        self._version = version if version and version != "None" else 1

    @property
    def kind(self) -> str:
        return self._kind

    @property
    def sequence(self) -> int:
        return self._sequence

    @property
    def version(self) -> int:
        return self._version

    def __repr__(self) -> str:
        return f"<{', '.join(map(lambda s: f'{str(s)[1:]}={getattr(self, s)}', self.__slots__))}>"

    def __str__(self) -> str:
        tmp = f"{self.kind}{self.sequence}"
        if self.version:
            tmp += f" V{self.version}"

        return tmp

class Song():
    __slots__ = ['_variant', '_title', '_url', '_artists', '_flags']

    def __init__(self, variant: SongVariant, title: str, url: str, artists: Optional[List[str]] = None, flags: Optional[List[str]] = None):
        self._variant = variant
        self._title = title
        self._url = url
        self._artists = artists if artists else []
        self._flags = flags if flags else []

    @property
    def variant(self) -> SongVariant:
        return self._variant

    @property
    def title(self) -> str:
        return self._title

    @property
    def url(self) -> str:
        return self._url

    @property
    def artists(self) -> List[str]:
        return self._artists

    def artists_str(self) -> str:
        return f"{', '.join(self.artists)}"

    @property
    def flags(self) -> List[str]:
        return self._flags

    def __repr__(self) -> str:
        return f"<{', '.join(map(lambda s: f'{str(s)[1:]}={getattr(self, s)}', self.__slots__))}>"

    def __str__(self) -> str:
        return f"[{str(self.variant)}] {self.title}"

class Anime():
    __slots__ = ['_title', '_url', '_cover', '_songs']

    def __init__(self, title: str, url: Optional[str] = None, cover: Optional[str] = None, songs: Optional[List[Song]] = None):
        self._title = title
        self._url = url if url and url != 'None' else 'https://anilist.co/search/anime'
        self._cover = cover if cover and cover != 'None' else 'https://files.catbox.moe/wgrm4k.png'
        self._songs = songs if songs else []

    @property
    def title(self) -> str:
        return self._title
    
    @property
    def url(self) -> str:
        return self._url

    @property
    def cover(self) -> str:
        return self._cover

    @property
    def songs(self) -> List[Song]:
        return self._songs

    def __repr__(self) -> str:
        return f"<{', '.join(map(lambda s: f'{str(s)[1:]}={getattr(self, s)}', self.__slots__))}>"


class Themes():

    class ThemesError(Exception):
        def __init__(self, status=000, message="Generic Themes Error"):
            self.message = message
            self.status = status
            super().__init__(self.message)
    
    class NoResultsError(Exception):
        def __init__(self, status=204, message="No Results"):
            self.message = message
            self.status = status
            super().__init__(self.message)

    @staticmethod
    async def search_animethemesmoe(show):
        url = f"https://api.animethemes.moe/search?q={show}&include[anime]=animethemes.animethemeentries.videos,resources,images,animethemes.song.artists&fields[anime]=name&fields[search]=anime&fields[resource]=link&fields[animetheme]=type,sequence&fields[animethemeentry]=version,nsfw,spoiler&fields[video]=basename&fields[image]=link&fields[song]=title&fields[artist]=name"
        
        async with Resources.session.get(url) as resp:
            if resp.status != 200:
                raise Themes.ThemesError(message=f"Bad response from animethemes.moe [{resp.status}]")
            try:
                res = await resp.json()
            except:
                raise Themes.ThemesError(message="I failed to parse response")
            else:
                if not res:
                    raise Themes.ThemesError(message="Err: empty response from animethemes.moe")
            if "errors" in res:
                raise Themes.ThemesError(status=res["errors"][0]["status"], message=res["errors"][0]["detail"])

            data = res["search"]["anime"]

            if not data:
                raise Themes.NoResultsError()

            try:
                data = process.extractOne({"name":show}, data, lambda d: d["name"])[0]
                songs = []
                for theme in data["animethemes"]:
                    kind = theme["type"]
                    num = theme["sequence"]
                    title = theme["song"]["title"]
                    artists = [a["name"] for a in theme["song"]["artists"]]
                    for song in theme["animethemeentries"]:
                        flags = []
                        if song["nsfw"]:
                            flags.append("NSFW")
                        if song["spoiler"]:
                            flags.append("Spoiler")
                        url = 'https://animethemes.moe'
                        if song['videos']:
                            url = f"https://animethemes.moe/video/{song['videos'][0]['basename']}"
                        else:
                            url = f"https://animethemes.moe/search?q={urllib.parse.quote_plus(show)}"
                        songs.append(
                            Song(
                                SongVariant(kind, num, song["version"]),
                                title,
                                url,
                                artists,
                                flags
                            )
                        )
            except:
                raise Themes.ThemesError(status=-1, message="Err: animethemes.moe response structure corrupt")

            return Anime(
                data["name"],
                data["resources"][1]['link'],
                data["images"][-1]['link'],
                songs
            )
