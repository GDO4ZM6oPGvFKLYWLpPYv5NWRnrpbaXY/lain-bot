from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Dict
    from .user import User
    from .data import FetchData

from bson import ObjectId
from .data import UserSearch, ResultStatus
from typing import TypeVar

user_id = TypeVar('user_id', bound=ObjectId)

class Query:
    """Responsible to getting data from 3rd party and formatting it into local
    format
    """
    MAX_USERS_PER_QUERY = 1 #: For queries supporting multiple users per query, 0 for unlimited

    async def find(self, username: str) -> UserSearch:
        """Try to find user from given username for service. Useful for services
        that use an id that isn't the username or when usernames could change

        Args:
            username: The username to search for
        
        Returns: The search result
        """
        return UserSearch(status=ResultStatus.MISSING)

    async def fetch(self, users: List[User] = [], tries: int = 3) -> Dict[user_id, FetchData]:
        """Fetch data for user(s) from service

        Args:
            users: The user(s) to fetch data for. Defaults to [].
            tries: Number of tries for queries supporting retries. Defaults to 3.

        Returns: Dict of user(s) (by discord id) and its query data
        """
        return {}
