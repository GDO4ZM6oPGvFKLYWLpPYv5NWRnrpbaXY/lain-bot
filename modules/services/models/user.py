from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from bson import ObjectId
    from .profile import Profile
    from typing import Dict, Type, Union, Any

from .. import Service

class UserStatus:
    INACTIVE = int(0)
    ACTIVE = int(1)

class User:
    """User from database

    Attributes:
        _id: MongoDB id
        discord_id: discord id of user
        status: database status of the document
        service: which service the document refers to
        service_id: id used when doing 3rd party api call to service
        profile: any extra 3rd party data to associate with user other than lists
        lists: lists used to store entry data for syncing
    """

    __slots__ = ['_id', 'discord_id', 'status', 'service', 'service_id', 'profile', 'lists']

    def __init__(
        self,
        _id:            ObjectId                    = None,
        discord_id:     str                         = None,
        status:         int                         = UserStatus.INACTIVE,
        service:        str                         = None,
        service_id:     Union[str, int]             = None,
        profile:        Type[Profile]               = None,
        lists:          Dict[str, Dict[str, Any]]   = {},
        **kwargs # ignore any extra fields entry might have
    ) -> None:
        self._id = _id
        self.discord_id = discord_id
        self.status = status
        self.service = service
        self.service_id = service_id

        self.profile = Service(service).profile(profile)
        self.lists = Service(service).lists(lists)

    @property
    def dict(self) -> Dict[str, Any]:
        return {
            'discord_id': self.discord_id,
            'status': self.status,
            'service': self.service,
            'service_id': self.service_id,
            'profile': self.profile.dict,
            'lists': self.lists,
        }
