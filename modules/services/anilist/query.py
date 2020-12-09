from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import List, Dict, Any
    from ..models.user import User

import re, asyncio, aiohttp
from ..models.query import Query, user_id
from ..models.data import FetchData, QueryResult, ResultStatus, UserSearch, EntryAttributes
from .entry import AnimeEntry, MangaEntry
from .profile import WeebProfile
from .enums import ScoreFormat, Status
from modules.core.resources import Resources

mangaListFields = '''
    {
        lists {
            entries {
                ...mediaFields
                progressVolumes
                media {
                    chapters
                    volumes
                }
            }
        }
    }
'''

animeListFields = '''
    {
        lists {
            entries {
                ...mediaFields
                media {
                    episodes
                }
            }
        }
    }
'''

userFields = '''
    {
        mediaListOptions {
            scoreFormat
        }
        name
        about
        avatar {
            large
        }
        bannerImage
        favourites {
            anime {
                nodes {
                    title {
                        romaji
                    }
                }
            }
        }
        statistics {
            anime {
                genres(sort:MEAN_SCORE_DESC) {
                    genre
                }
            }
        }
    }
'''

userFieldsId = '''
    {
        mediaListOptions {
            scoreFormat
        }
        name
        id
        about
        avatar {
            large
        }
        bannerImage
        favourites {
            anime {
                nodes {
                    title {
                        romaji
                    }
                }
            }
        }
        statistics {
            anime {
                genres(sort:MEAN_SCORE_DESC) {
                    genre
                }
            }
        }
    }
'''

fragments = '''
    fragment mediaFields on MediaList {
        status
        mediaId
        score
        progress
        media {
            countryOfOrigin
            format
            isAdult
            bannerImage
            coverImage {
                large
            }
            title {
                romaji
            }
        }
    }
'''

def compute_lines_per_user():
    # first line is empty
    m = len(mangaListFields.split('\n'))-1
    a = len(animeListFields.split('\n'))-1
    p = len(userFields.split('\n'))-1

    return m+a+p

lines_per_user = compute_lines_per_user()

# anilist limits single query to 500 complexity
def compute_complexity():
    pieces = [animeListFields, mangaListFields, userFields]
    frags = get_fragment_complexities()

    # add in any complexity the fragments are to each pice that has a fragment
    complexity = 0
    for piece in pieces:
        for frag in frags:
            complexity += piece.count(frag)*frags[frag]
            piece = piece.replace(frag, '')
        complexity += len(extract_complexities(piece))

    complexity += len(pieces) # each piece is one complexity
    return complexity

def get_fragment_complexities():
    # fancy regex to get list of all fragment names
    frags = list(re.finditer(r'(?:fragment )(?P<frag_name>[a-zA-Z]+)(?: on [a-zA-Z]+)', fragments))
    frag_comp = {}
    num_frags = len(frags)
    # get complexity of each fragment
    for x in range(0, num_frags):
        frag = frags[x]
        frag_fields = None
        # use regex span info to get start line of where fragment was found and start line of where next fragment begins
        if x+1 < num_frags:
            frag_fields = fragments[frags[x].span()[1]:frags[x+1].span()[0]]
        else:
            frag_fields = fragments[frags[x].span()[1]:]

        frag_comp['...'+frag.group('frag_name')] = len(extract_complexities(frag_fields))

    return frag_comp

def extract_complexities(s):
    # return list of all the complexities
    # each field and parameter is 1 complexity
    s = re.sub(r'\(.+\)', ' ', s)
    s = re.sub(' +', ' ', re.sub('\n|{|}', ' ', s)).strip()
    return [s for s in s.split(' ') if s]

query_complexity = compute_complexity()
anilist_max_complexity = 500

class AnilistQuery(Query):
    MAX_USERS_PER_QUERY = anilist_max_complexity // query_complexity

    def _build_query(self, ids):
        """helper to build query for given list of ids"""
        if not ids:
            return None

        built_query = 'query {\n'
        for user in ids:
            built_query += f"profile_{user}: User(id:{user}){userFields}"
            built_query += f"animelist_{user}: MediaListCollection(userId:{user}, type:ANIME){animeListFields}"
            built_query += f"mangalist_{user}: MediaListCollection(userId:{user}, type:MANGA){mangaListFields}"
        built_query += f"}}{fragments}"
        
        return built_query

    def _serach_query(self, username):
        built_query = 'query {\n'
        built_query += f"profile: User(name:\"{username}\"){userFieldsId}"
        built_query += f"animelist: MediaListCollection(userName:\"{username}\", type:ANIME){animeListFields}"
        built_query += f"mangalist: MediaListCollection(userName:\"{username}\", type:MANGA){mangaListFields}"
        built_query += f"}}{fragments}"
        
        return built_query

    async def find(self, username: str) -> UserSearch:
        if not username:
            return UserSearch(status=ResultStatus.ERROR, data='No username provided')

        try:
            async with Resources.syncer_session.post('https://graphql.anilist.co', json={'query':self._serach_query(username)}, raise_for_status=False, timeout=aiohttp.ClientTimeout(total=5)) as resp:
                # handle non 200 status
                if resp.status == 404:
                    return UserSearch(status=ResultStatus.NOTFOUND, data=None)
                if resp.status == 429:
                    return UserSearch(status=ResultStatus.ERROR, data='Anilist is rate limiting me. Try again later')
                try:
                    resp.raise_for_status()
                except Exception as e:
                    return UserSearch(status=ResultStatus.ERROR, data=e.message)
                if resp.status != 200:
                    return UserSearch(status=ResultStatus.ERROR, data=f'Not working right now. status: {resp.status}')

                data = (await resp.json()).get('data')

                profile = data.get(f"profile")
                animelist = data.get(f"animelist")
                mangalist = data.get(f"mangalist")

                if profile == None or animelist == None or mangalist == None: # oof
                    return UserSearch(status=ResultStatus.ERROR, data='I failed at reading data')

                d = FetchData(
                    lists={
                        'anime': self._gen_animelist(animelist),
                        'manga': self._gen_mangalist(mangalist)
                    },
                    profile=self._gen_profile(profile)
                )

                return UserSearch(
                    status=ResultStatus.OK, 
                    id=profile['id'],
                    image=profile['avatar']['large'],
                    link=f"https://anilist.co/user/{username}",
                    data=d
                )
        except aiohttp.ServerTimeoutError:
            return UserSearch(status=ResultStatus.ERROR, data="Connecting to anilist took to long. Try again later")
        except aiohttp.ClientError as e:
            return UserSearch(status=ResultStatus.ERROR, data=f"I couln't connect to anilist: {e.message}")
        except Exception:
            # TODO: logger
            return UserSearch(status=ResultStatus.ERROR, data=f"I failed")

    async def fetch(self, users: List[User] = [], tries: int = 3) -> Dict[user_id, FetchData]:
        if not users or tries < 1:
            return {}

        query_ids = [u.service_id for u in users]
        while tries:
            tries -= 1
            q = self._build_query(query_ids)
            if not q: return {} # all the users failed
            try:
                async with Resources.syncer_session.post('https://graphql.anilist.co', json={'query':q}, raise_for_status=False, timeout=aiohttp.ClientTimeout(total=20)) as resp:

                    # too many request but still have more tries -> try next time anilist says it'll accept request
                    if tries and resp.status == 429:
                        wait_time = 60 # rate limiting should reset after minute at latest
                        try: wait_time = int(resp.headers['Retry-After']) # use provided wait time from anilist if there
                        except: pass

                        await asyncio.sleep(wait_time)
                        continue # retry

                    # bad request that probably won't work after retry
                    # maybe API changed so query needs updating, anilist down, etc.
                    if resp.status not in [200, 404]: 
                        # TODO: log
                        return {}

                    data = None
                    try: data = await resp.json()
                    except: pass

                    if not data: # parsing failed or got gobbledygook 
                        # TODO: log
                        await asyncio.sleep(10) # we'll just try again after a little bit of time and see what happends
                        continue 
                    
                    # expected, well-formatted data from here on

                    # purge users with errors and go next
                    bad_ids = []
                    errors = data.get('errors')
                    if errors:
                        for error in errors:
                            locations = error.get('locations') # which lines caused query error
                            if locations:
                                idx = (locations[0]['line'] - 2) // lines_per_user # which index in query_id array is this location associated with
                                if 0 <= idx < len(query_ids): # just being careful
                                    # TODO: log
                                    bad_ids.append(query_ids[idx])

                    if bad_ids:
                        query_ids = list(set(query_ids) - set(bad_ids))
                        continue # retry
                    
                    data = data.get('data')

                    if not data: # lack of data where it should be
                        # I don't see this actually happening so we'll just stop trying and return blanks
                        # TODO: log
                        return {}

                    try:
                        return await asyncio.get_running_loop().run_in_executor(
                            None,
                            self._get_data,
                            users,
                            data
                        )
                    except:
                        return {}

            except: # some sort of connection error
                if tries: await asyncio.sleep(10) # wait a little and try again
        return {} # all requests failed

    def _get_data(self, users: List[User], data: Dict[str, Any]) -> Dict[user_id, FetchData]:
        ret = {}
        for user in users:
            profile = data.get(f"profile_{user.service_id}")
            animelist = data.get(f"animelist_{user.service_id}")
            mangalist = data.get(f"mangalist_{user.service_id}")

            if profile == None or animelist == None or mangalist == None: # id not present (probably removed because it had query error)
                continue # go next

            ret[user._id] = FetchData(
                lists={
                    'anime': self._gen_animelist(animelist),
                    'manga': self._gen_mangalist(mangalist)
                },
                profile=self._gen_profile(profile)
            )
        return ret

    def _gen_animelist(self, data) -> QueryResult:
        if data == None:
            return QueryResult(status=ResultStatus.ERROR, data='Anilist animelist generator given None data')

        lst = []
        try:
            for sublst in data['lists']:
                for entry in sublst['entries']:
                    media = AnimeEntry()
                    media['id'] = entry.get('mediaId')
                    media['banner'] = entry['media']['bannerImage']
                    media['cover'] = entry['media']['coverImage']['large']
                    media['title'] = entry['media']['title']['romaji']
                    media['episodes'] = entry['media']['episodes']
                    media['score'] = entry['score']
                    media['episode_progress'] = entry['progress']
                    media['status'] = self._convert_status(entry['status'])
                    media['attributes'] = 0
                    if entry['media']['format'] == 'MUSIC':
                        media['attributes'] = media['attributes'] | EntryAttributes.song
                    if entry['media']['isAdult']:
                        media['attributes'] = media['attributes'] | EntryAttributes.adult
                    lst.append(media)
        except Exception as e:
            return QueryResult(
                status=ResultStatus.ERROR, 
                data=f"Exception raised generating animelist from anilist data.\n{e.message}"
            )

        return QueryResult(
            status=ResultStatus.OK, 
            data=lst
        )

    def _gen_mangalist(self, data) -> QueryResult:
        if data == None:
            return QueryResult(status=ResultStatus.ERROR, data='Anilist mangalist generator given None data')

        lst = []
        try:
            for sublst in data['lists']:
                for entry in sublst['entries']:
                    media = MangaEntry()
                    media['id'] = entry.get('mediaId')
                    media['banner'] = entry['media']['bannerImage']
                    media['cover'] = entry['media']['coverImage']['large']
                    media['title'] = entry['media']['title']['romaji']
                    media['chapters'] = entry['media']['chapters']
                    media['volumes'] = entry['media']['volumes']
                    media['score'] = entry['score']
                    media['chapter_progress'] = entry['progress']
                    media['volume_progress'] = entry['progressVolumes']
                    media['status'] = self._convert_status(entry['status'])
                    media['attributes'] = 0
                    if entry['media']['countryOfOrigin'] == 'KR':
                        media['attributes'] = media['attributes'] | EntryAttributes.manhwa
                    if entry['media']['countryOfOrigin'] == 'CN':
                        media['attributes'] = media['attributes'] | EntryAttributes.manhua
                    if entry['media']['isAdult']:
                        media['attributes'] = media['attributes'] | EntryAttributes.adult
                    lst.append(media)
        except Exception as e:
            return QueryResult(
                status=ResultStatus.ERROR, 
                data=f"Exception raised generating mangalist from anilist data.\n{e.message}"
            )

        return QueryResult(
            status=ResultStatus.OK, 
            data=lst
        )

    def _gen_profile(self, data) -> QueryResult:
        if data == None:
            return QueryResult(status=ResultStatus.ERROR, data='Anilist profile generator given None data')

        genres = []
        try:
            for g in data['statistics']['anime']['genres'][:5]: # top 5 genres by average user score of anime in that genre
                genres.append(g['genre'])
        except:
            pass

        fav = []
        try:
            for f in data['favourites']['anime']['nodes']:
                fav.append(f['title']['romaji'])
        except:
            pass

        try:
            prof = WeebProfile(
                name=data['name'],
                avatar = data['avatar']['large'],
                score_format = self._convert_score_format(data['mediaListOptions']['scoreFormat']),
                about = data['about'],
                banner = data['bannerImage'],
                favourites = fav,
                genres = genres
            )
        except Exception as e:
            return QueryResult(
                status=ResultStatus.ERROR, 
                data=f"Exception raised generating profile from anilist data.\n{e.message}"
            )

        return QueryResult(
            status=ResultStatus.OK, 
            data=prof
        )

    def _convert_score_format(self, format):
        if format == 'POINT_10':
            return ScoreFormat.POINT_10
        elif format == 'POINT_100':
            return ScoreFormat.POINT_100
        elif format == 'POINT_10_DECIMAL':
            return ScoreFormat.POINT_10_DECIMAL
        elif format == 'POINT_5':
            return ScoreFormat.POINT_5
        elif format == 'POINT_3':
            return ScoreFormat.EMOJI
        else:
            return ScoreFormat._BASE

    def _convert_status(self, status):
        if status == 'CURRENT':
            return Status.CURRENT
        elif status == 'PLANNING':
            return Status.PLANNING
        elif status == 'COMPLETED':
            return Status.COMPLETED
        elif status == 'DROPPED':
            return Status.DROPPED
        elif status == 'PAUSED':
            return Status.PAUSED
        elif status == 'REPEATING':
            return Status.REPEATING
        else:
            return Status.UNKNOWN