from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Dict, Union, List, Type
    from .entry import ListEntry
    from .profile import Profile

from dataclasses import dataclass
from enum import Enum, auto, IntFlag

class EntryAttributes(IntFlag):
    # syncer uses (via Comprehension) to ignore displaying changes associated
    # with entries having cetain attrbiutes on a per guild basis.
    adult = 1
    manhwa = 2
    manhua = 4
    song = 8

    ## these are mainly for my reference ##

    @staticmethod
    def apply_flags(meta, *tags):
        for tag in tags:
            meta = meta | tag
        return meta
    
    @staticmethod
    def unset_flags(meta, *tags):
        for tag in tags:
            meta = meta & ~tag
        return meta

    @staticmethod
    def toggle_flags(meta, *tags):
        for tag in tags:
            meta = meta ^ tag
        return meta

class ResultStatus(Enum):
    OK = auto()         # data successfuly packaged (guranteed to have data populated)
    SKIP = auto()       # intentionally ignore
    MISSING = auto()    # no data to package
    ERROR = auto()      # error occured packaging data
    NOTFOUND = auto()   # used by user search when user not found
    FOUND = auto()      # used by user search as OK and user found (guranteed to have data populated)

@dataclass
class QueryResult:
    __slots__ = ['status', 'data']
    status: ResultStatus
    data: Union[None, List[Type[ListEntry]], str, Type[Profile]]

@dataclass
class FetchData:
    __slots__ = ['lists', 'profile']
    lists: Dict[str, QueryResult]
    profile: QueryResult

@dataclass
class Image:
    narrow: str = ''
    wide: str = ''

@dataclass
class UserSearch:
    status: ResultStatus
    id: Union[str, int, None] = None
    image: str = ''
    link: str = ''
    data: Union[None, str, FetchData] = None