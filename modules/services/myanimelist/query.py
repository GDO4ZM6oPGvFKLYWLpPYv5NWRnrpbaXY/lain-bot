from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Dict
    from ..models.user import User

from modules.core.resources import Resources
from ..models.query import Query, user_id
from ..models.data import EntryAttributes, FetchData, QueryResult, ResultStatus, UserSearch
from ..anilist.entry import AnimeEntry, MangaEntry
from .profile import MALProfile
from ..anilist.enums import ScoreFormat, Status
import asyncio, datetime

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
            print(e)
            return {}

    async def _gen_profile(self, user: User, animelist, mangalist) -> QueryResult:
        diff = datetime.datetime.now() - user.profile.last_profile_update
        # data used for profile rarely changes so don't fetch more than once per 24hrs*2 to reduce api calls
        if not(diff.days or diff.seconds > 86400*2):
            if animelist.status == ResultStatus.OK:
                user.profile.last_anime_update = datetime.datetime.now()
            if mangalist.status == ResultStatus.OK:
                user.profile.last_manga_update = datetime.datetime.now()
            return QueryResult(status=ResultStatus.OK, data=user.profile)

        data = await self._fetch_profile(user.service_id)
        data = self._profile(data)
        if data.status != ResultStatus.OK:
            if animelist.status == ResultStatus.OK:
                user.profile.last_anime_update = datetime.datetime.now()
            if mangalist.status == ResultStatus.OK:
                user.profile.last_manga_update = datetime.datetime.now()
            return QueryResult(status=ResultStatus.OK, data=user.profile)
        else:
            if animelist.status == ResultStatus.OK:
                data.data.last_anime_update = datetime.datetime.now()
            if mangalist.status == ResultStatus.OK:
                data.data.last_manga_update = datetime.datetime.now()
            data.data.last_profile_update = datetime.datetime.now()
            return data

    async def _gen_animelist(self, user: User) -> QueryResult:
        diff = datetime.datetime.now() - user.profile.last_anime_update
        # jikan caches request for an hour so there's no point in fetching any faster
        if not(diff.days or diff.seconds > 3600):
            return QueryResult(status=ResultStatus.SKIP, data=None)

        data = await self._fetch_list(user.service_id, 'anime')
        return self._animelist(data)

    async def _gen_mangalist(self, user: User) -> QueryResult:
        diff = datetime.datetime.now() - user.profile.last_manga_update
        # jikan caches request for an hour so there's no point in fetching any faster
        if not(diff.days or diff.seconds > 3600):
            return QueryResult(status=ResultStatus.SKIP, data=None)

        data = await self._fetch_list(user.service_id, 'manga')
        return self._mangalist(data)

    async def _fetch_list(self, id, kind: str):
        """get well-formated list from myanimelist"""
        lst = []
        # jikan paginates lists into groups of 300
        # build complete list by combinig list from each page
        page = 1
        partial_lst = await self._fetch_partial_list(id, kind, page)
        limit = 50  # safety for preventing infinite loop, theoretically this could go up to a list with 15000 entries
        while limit:
            limit -= 1
            if not partial_lst: # good request but empty list, we have all the list data
                break
            lst.extend(partial_lst)
            await asyncio.sleep(4) # adhere to jikan rate limits
            page += 1
            partial_lst = await self._fetch_partial_list(id, kind, page)
        return lst

    async def _fetch_partial_list(self, id, kind, page):
        """get list from myanimelist via jikan api"""
        async with Resources.syncer_session.get(f"https://api.jikan.moe/v3/user/{id}/{kind}list/all/{page}", raise_for_status=True) as resp:
            if resp.status != 200:
                raise Exception('Bad response from myanimelist Jikan call')
            data = await resp.json()
            return data.get(kind)

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
                media['id'] = entry.get('mal_id')
                media['cover'] = entry.get('image_url')
                media['title'] = entry.get('title')
                media['episodes'] = entry.get('total_episodes')
                media['score'] = entry.get('score')
                media['episode_progress'] = entry.get('watched_episodes')
                media['status'] = self._convert_status(entry.get('watching_status'))
                media['attributes'] = 0
                if entry['type'] == 'Music':
                    media['attributes'] = media['attributes'] | EntryAttributes.song
                if entry['rating'] == 'Rx': 
                # ['R', 'R+', 'Rx'] also exist but for reference Attack on Titan is R on MAL
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
                media['id'] = entry.get('mal_id')
                media['cover'] = entry.get('image_url')
                media['title'] = entry.get('title')
                media['chapters'] = entry.get('total_chapters')
                media['volumes'] = entry.get('total_volumes')
                media['score'] = entry.get('score')
                media['chapter_progress'] = entry.get('read_chapters')
                media['volume_progress'] = entry.get('read_volumes')
                media['status'] = self._convert_status(entry.get('reading_status'))
                media['attributes'] = 0
                if entry['type'] == 'Manhwa':
                    media['attributes'] = media['attributes'] | EntryAttributes.manhwa
                if entry['type'] == 'Manhua':
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

        fav = []
        try:
            for f in data['favorites']['anime']:
                fav.append(f['name'])
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