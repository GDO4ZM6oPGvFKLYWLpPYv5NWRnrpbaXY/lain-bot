from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import List, Dict, Any

from .enums import ScoreFormat
from ..models.profile import Profile

class WeebProfile(Profile):
    __slots__ = ['name', 'avatar', 'score_format', 'about', 'banner', 'favourites', 'genres']

    def __init__(
        self, 
        name:           str         = '',
        avatar:         str         = '',
        score_format:   str         = '', 
        about:          str         = '', 
        banner:         str         = '', 
        favourites:     List[str]   = [], 
        genres:         List[str]   = [],
        **kwargs
    ) -> None:
        self.name = name
        self.avatar = avatar if avatar else 'https://files.catbox.moe/suqy48.png'
        self.score_format = score_format if score_format else ScoreFormat.POINT_10
        self.about = about
        self.banner = banner
        self.favourites = favourites
        self.genres = genres

    @property
    def dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'avatar': self.avatar,
            'score_format': self.score_format,
            'about': self.about,
            'banner': self.banner,
            'favourites': self.favourites,
            'genres': self.genres
        }

    def __repr__(self):
        return f"<{str(self)}>"

    def __str__(self):
        return f"name={self.name}, avatar={self.avatar}, score_format={self.score_format}, about='{self.about}', banner='{self.banner}', favourites={self.favourites}, genres={self.genres}"