from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, Any

from ..anilist.profile import WeebProfile
import datetime

class MALProfile(WeebProfile):
    __slots__ = ['last_profile_update']

    def __init__(
        self, 
        *args,
        last_profile_update: datetime.datetime = datetime.datetime(1969, 4, 20),
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)
        self.last_profile_update = last_profile_update

    @property
    def dict(self) -> Dict[str, Any]:
        d = super().dict
        d['last_profile_update'] = self.last_profile_update
        return d

