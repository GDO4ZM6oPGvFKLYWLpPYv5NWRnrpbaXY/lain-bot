import logging
logger = logging.getLogger(__name__)

class Anilist2:

    class AnilistBadArguments(Exception):
        def __init__(self, message="Invalid arguments passed to function"):
            self.message = message
            super().__init__(self.message)

    class AnilistError(Exception):
        def __init__(self, status=000, message="Anilist Generic Error"):
            self.message = message
            self.status = status
            super().__init__(self.message)

    apiUrl = 'https://graphql.anilist.co'

    mediaQuery = '''
        query(
            $id: Int,
            $search: String,
            $asHtml: Boolean,
            $isManga: Boolean!,
            $isAnime: Boolean!,
            $isCharacter: Boolean!,
            $isLN: Boolean!,
            $isMain: Boolean,
        ) {
            manga: Media(id: $id, search: $search, type: MANGA, format_not:NOVEL) @include(if: $isManga) {
                ...genericMediaFields
                chapters
            }
            ln: Media(id: $id, search: $search, type: MANGA, format:NOVEL) @include(if: $isLN) {
                ...genericMediaFields
                chapters
            }
            anime: Media(id: $id, search: $search, type: ANIME) @include(if: $isAnime) {
                ...genericMediaFields
                episodes
                duration
                studios(isMain: $isMain) {
                    nodes {
                        name
                        siteUrl
                    }
                }
            }
            character: Character(id: $id, search: $search) @include(if: $isCharacter) {
                ...characterFields
            }
        }

        fragment genericMediaFields on Media {
            id
            idMal
            title {
                romaji
            }
            status
            description(asHtml: $asHtml)
            startDate {
                year
                month
                day
            }
            endDate {
                year
                month
                day
            }
            season
            format
            seasonYear
            coverImage {
                extraLarge
                large
            }
            bannerImage
            genres
            meanScore
            popularity
            siteUrl
        }

        fragment characterFields on Character {
            id
            name {
                full
                alternative
            }
            image {
                large
            }
            description
            media {
                nodes {
                title {
                    romaji
                }
                coverImage {
                    medium
                }
                siteUrl
                }
            }
            siteUrl
        }
        '''

    async def aniSearch(session, search, isManga=False, isAnime=False, isCharacter=False, isLN=False):
        """Search anilist for manga, anime, and/or character

        Args:
            session (aiohttp.ClientSession): A session for making post requests. Expected to be from aiohttp.ClientSession()
            search (str): The anilist search string
            isManga (bool): If the results should contain a manga entry
            isAnime (bool): If the results should contain an anime entry
            isCharacter (bool): If the results should contain a character entry
            isLN (bool): If the reuslts should montain a ligh novel entry

        Returns:
            A valid anilist query response.

        Raises:
            AnilistBadArguments: If valid session or search not supplied
            AnilistError: If valid reponse was not obtained
        """
        if not (session and (isManga or isAnime or isCharacter or isLN)):
            raise Anilist2.AnilistBadArguments()

        v = {
            'search': search,
            'isManga': isManga,
            'isAnime': isAnime,
            'isCharacter': isCharacter,
            'isLN': isLN,
        }

        if isManga or isLN:
            v['asHtml'] = False

        if isAnime:
            v['asHtml'] = False
            v['isMain'] = True

        return await Anilist2.__request(session, Anilist2.mediaQuery, v)


    async def __request(session, query, variables):
        async with session.post(Anilist2.apiUrl, json={'query': query, 'variables': variables}, raise_for_status=False) as resp:
            logger.debug("POST with vars %s returned status %s" % (variables,
                resp.status))
            return await Anilist2.__resolveResponse(resp)


    async def __resolveResponse(resp):
        """Tries to resolve response into well-formatted json derived dictionary.

        Args:
            resp (aiohttp.ClientResponse): The response to resolve

        Returns:
            A valid json response as dictionary. Otherwise, None

        Raises:
            AnilistError: If valid reponse was not obtained
        """

        if not resp:
            raise Anilist2.AnilistError('No response')

        if resp.status == 500:
            raise Anilist2.AnilistError(500, 'AniList internal service error')

        if resp.status == 503:
            raise Anilist2.AnilistError(503,
                'Anilist is currently unreachable at the moment')

        if resp.status == 404:
            raise Anilist2.AnilistError(404, 'Query yielded no results')

        if resp.status == 429:
            raise Anilist2.AnilistError(429, 'Too many requests')

        if resp.status != 200:
            raise Anilist2.AnilistError(resp.status, 'Response failure')

        try:
            ret = await resp.json()
        except:
            raise Anilist2.AnilistError('Could not parse json from response')
        else:
            return ret
