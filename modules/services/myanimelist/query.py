from __future__ import annotations
import logging
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Dict
    from ..models.user import User

from modules.core.resources import Resources
from ..models.query import Query, user_id
from ..models.data import EntryAttributes, FetchData, QueryResult, ResultStatus, UserSearch, Image
from ..anilist.entry import AnimeEntry, MangaEntry
from .profile import MALProfile
from ..anilist.enums import ScoreFormat, Status
import datetime, logging, types

logger = logging.getLogger(__name__)

def img_a(self) -> List[Image]:
    if self['cover']:
        try:
            link = self['cover']
            link = link.split('.jpg?s')[0]
            link = link.split('/')
            link = f"https://cdn.myanimelist.net/images/anime/{link[-2]}/{link[-1]}l.webp"
            return [Image(narrow=link, wide=link)]
        except:
            return []
    else:
        return []

def img_m(self) -> List[Image]:
    if self['cover']:
        try:
            link = self['cover']
            link = link.split('.jpg?s')[0]
            link = link.split('/')
            link = f"https://cdn.myanimelist.net/images/manga/{link[-2]}/{link[-1]}l.webp"
            return [Image(narrow=link, wide=link)]
        except:
            return []
    else:
        return []

class MyAnimeListQuery(Query):
    MAX_USERS_PER_QUERY = 1

    async def find(self, username: str) -> UserSearch:
        if not username:
            return UserSearch(status=ResultStatus.ERROR, data='No username provided')

        data = None
        async with Resources.syncer_session.get(f"https://api.jikan.moe/v3/user/{username}", raise_for_status=False) as resp:
            if resp.status == 404:
                return UserSearch(status=ResultStatus.ERROR, data='I couldn\'t find a user on mal with that name')
            if resp.status == 500:
                return UserSearch(status=ResultStatus.ERROR, data='I\'ve done too many mal requests too fast. Try again later')
            if resp.status == 503:
                return UserSearch(status=ResultStatus.ERROR, data='Looks like mal might be down. Try again later')
            
            try:
                resp.raise_for_status()
            except Exception as e:
                return UserSearch(status=ResultStatus.ERROR, data=f"Error! {e.message}")

            if resp.status != 200:
                return UserSearch(status=ResultStatus.ERROR, data=f'Not working right now. status: {resp.status}')

            try:
                data = await resp.json()
            except:
                return UserSearch(status=ResultStatus.ERROR, data=f"I couldn't read the data from myanimelist. Try again later")

        prof = self._profile(data)

        if prof.status != ResultStatus.OK:
            return UserSearch(status=ResultStatus.ERROR, data=prof.data)

        prof.data.last_profile_update = datetime.datetime.now()

        d = FetchData(
            lists={
                'anime': QueryResult(status=ResultStatus.OK, data=[AnimeEntry()]), # empty entry hints to skip first sync
                'manga': QueryResult(status=ResultStatus.SKIP, data=None)
            },
            profile=prof
        )

        return UserSearch(
            status=ResultStatus.OK, 
            id=username,
            image=prof.data.avatar,
            link=f"https://myanimelist.net/profile/{username}",
            data=d
        )

    async def fetch(self, users: List[User] = [], tries: int = 3) -> Dict[user_id, FetchData]:
        if not users or tries < 1:
            return {}
        user = users[0]

        try:
            animelist = await self._gen_animelist(user)
            mangalist = await self._gen_mangalist(user)
            return {
                user._id: FetchData(
                    lists={
                        'anime': animelist,
                        'manga': mangalist
                    },
                    profile= await self._gen_profile(user, animelist, mangalist)
                )
            }
        except Exception as e:
            logger.exception(str(e))
            return {}

    async def _gen_profile(self, user: User, animelist, mangalist) -> QueryResult:
        diff = datetime.datetime.now() - user.profile.last_profile_update
        # users requests cached for 5 mins, don't fetch more than once per 
        # 5 min to reduce fetches. cached requests don't count against rate
        # limits, but why waste time making request for stale data
        if not(diff.days or diff.seconds > 300):
            return QueryResult(status=ResultStatus.OK, data=user.profile)

        data = await self._fetch_profile(user.service_id)
        data = self._profile(data)
        if data.status != ResultStatus.OK:
            return QueryResult(status=ResultStatus.OK, data=user.profile)
        else:
            data.data.last_profile_update = datetime.datetime.now()
            return data

    async def _gen_animelist(self, user: User) -> QueryResult:
        data = await self._fetch_list(user.service_id, 'anime')
        return self._animelist(data)

    async def _gen_mangalist(self, user: User) -> QueryResult:
        data = await self._fetch_list(user.service_id, 'manga')
        return self._mangalist(data)

    async def _fetch_list(self, id, kind: str):
        """get well-formated list from myanimelist"""
        lst = []
        # mal sends up to 300 entries in a response
        # build complete list by combinig entries from multiple responses
        page = 0
        partial_lst = await self._fetch_partial_list(id, kind, page)
        limit = 50  # safety for preventing infinite loop, theoretically this could go up to a list with 15000 entries
        while page < limit:
            page += 1
            if not partial_lst: # good request but empty list, we have all the list data
                break
            lst.extend(partial_lst)
            # await asyncio.sleep(0.5) # idk rate limits for this endpoint
            partial_lst = await self._fetch_partial_list(id, kind, page*300)
        return lst

    async def _fetch_partial_list(self, id, kind, page):
        """get list from myanimelist via jikan api"""
        async with Resources.syncer_session.get(f"https://myanimelist.net/{kind}list/{id}/load.json?offset={page}", raise_for_status=True) as resp:
            if resp.status != 200:
                raise Exception('Bad response from myanimelist call')
            return await resp.json()

    async def _fetch_profile(self, id):
        """get profile from myanimelist via jikan api"""
        async with Resources.syncer_session.get(f"https://api.jikan.moe/v3/user/{id}", raise_for_status=True) as resp:
            if resp.status != 200:
                raise Exception('Bad response from myanimelist Jikan call')
            return await resp.json()

    def _animelist(self, data) -> QueryResult:
        if data == None:
            return QueryResult(status=ResultStatus.ERROR, data='Myanimelist animelist generator given None data')

        lst = []
        try:
            for entry in data:
                media = AnimeEntry()
                media.images = types.MethodType(img_a, media)
                media['id'] = entry.get('anime_id')
                media['cover'] = entry.get('anime_image_path')
                media['title'] = entry.get('anime_title')
                media['episodes'] = entry.get('anime_num_episodes')
                media['score'] = entry.get('score')
                media['episode_progress'] = entry.get('num_watched_episodes')
                media['status'] = self._convert_status(entry.get('status'))
                media['attributes'] = 0
                if entry['anime_media_type_string'] == 'Music':
                    media['attributes'] = media['attributes'] | EntryAttributes.song
                if entry['anime_mpaa_rating_string'] == 'Rx': 
                # ['R', 'R+', 'Rx'] also exist but for reference Attack on Titan is R and Akira is R+ on MAL
                    media['attributes'] = media['attributes'] | EntryAttributes.adult
                lst.append(media)
        except Exception as e:
            return QueryResult(
                status=ResultStatus.ERROR, 
                data=f"Exception raised generating animelist from mal data.\n{e.message}"
            )

        return QueryResult(
            status=ResultStatus.OK, 
            data=lst
        )

    def _mangalist(self, data) -> QueryResult:
        if data == None:
            return QueryResult(status=ResultStatus.ERROR, data='Myanimelist mangalist generator given None data')

        lst = []
        try:
            for entry in data:
                media = MangaEntry()
                media.images = types.MethodType(img_m, media)
                media['id'] = entry.get('manga_id')
                media['cover'] = entry.get('manga_image_path')
                media['title'] = entry.get('manga_title')
                media['chapters'] = entry.get('manga_num_chapters')
                media['volumes'] = entry.get('manga_num_volumes')
                media['score'] = entry.get('score')
                media['chapter_progress'] = entry.get('num_read_chapters')
                media['volume_progress'] = entry.get('num_read_volumes')
                media['status'] = self._convert_status(entry.get('status'))
                media['attributes'] = 0
                if entry['manga_media_type_string'] == 'Manhwa':
                    media['attributes'] = media['attributes'] | EntryAttributes.manhwa
                if entry['manga_media_type_string'] == 'Manhua':
                    media['attributes'] = media['attributes'] | EntryAttributes.manhua
                # if entry['type'] == 'Doujinshi':
                #     media['attributes'] = media['attributes'] | EntryAttributes.adult
                # maybe do this if you want some attributing but I'd rather 
                # allow some frisky stuff than hit false positives on lots of doujin
                # MAL doesn't allow 18+ images anyway so the attribute is kinda mute
                lst.append(media)
        except Exception as e:
            return QueryResult(
                status=ResultStatus.ERROR, 
                data=f"Exception raised generating mangalist from mal data.\n{e.message}"
            )

        return QueryResult(
            status=ResultStatus.OK, 
            data=lst
        )

    def _profile(self, data) -> QueryResult:
        if data == None:
            return QueryResult(status=ResultStatus.ERROR, data='Myanimelist profile generator given None')

        fav = {}
        try:
            for f in data['favorites']['anime']:
                fav[str(f['mal_id'])] = f['name']
        except:
            pass

        try:
            prof = MALProfile(
                name=data['username'],
                avatar = data['image_url'],
                score_format = ScoreFormat.POINT_10,
                about = data['about'],
                favourites = fav,
            )
        except Exception as e:
            return QueryResult(
                status=ResultStatus.ERROR, 
                data=f"Exception raised generating profile from mal data.\n{e.message}"
            )

        return QueryResult(
            status=ResultStatus.OK, 
            data=prof
        )

    def _convert_status(self, status):
        """mal status to db status"""
        if not status: return Status.UNKNOWN
        if status == 1:
            return Status.CURRENT
        elif status == 2:
            return Status.COMPLETED
        elif status == 3:
            return Status.PAUSED
        elif status == 4:
            return Status.DROPPED
        elif status == 6:
            return Status.PLANNING
        else:
            return Status.UNKNOWN