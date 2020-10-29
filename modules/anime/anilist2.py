import logging
logger = logging.getLogger(__name__)

class Anilist2:

    class AnilistBadArguments(Exception):
        def __init__(self, message="Invalid arguments passed to function"):
            self.message = message
            super().__init__(self.message)

    class AnilistError(Exception):
        def __init__(self, status, message="Anilist Generic Error"):
            self.message = message
            self.status = status
            super().__init__(self.message)

    class AnilistQueryNotResultsError(AnilistError):
        def __init__(self, status=404, message="Query yielded no results"):
            self.message = message
            self.status = status
            super().__init__(status, self.message)

    class AnilistDownError(AnilistError):
        def __init__(self, status=503, message="Anilist is currently unreachable at the moment"):
            self.message = message
            self.status = status
            super().__init__(status, self.message)

    apiUrl = 'https://graphql.anilist.co'

    userDataQuery = '''
        query($id: Int) {
            User(id:$id) {
                name
                mediaListOptions {
                    scoreFormat
                }
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
                        count
                        meanScore
                        genres(limit:5, sort:COUNT_DESC) {
                            genre
                        }
                    }
                }
            }
            animeList: MediaListCollection(userId:$id, type:ANIME){
                lists {
                    entries {
                        status
                        mediaId
                        score
                        progress
                        media {
                            bannerImage
                            coverImage {
                                large
                            }
                            episodes
                            title {
                                romaji
                            }
                        }
                    }
                }
            }
            mangaList: MediaListCollection(userId:$id, type:MANGA){
                lists {
                    entries {
                        status
                        mediaId
                        score
                        progress
                        progressVolumes
                        media {
                            bannerImage
                            coverImage {
                                large
                            }
                            chapters
                            volumes
                            title {
                                romaji
                            }
                        }
                    }
                }
            }
        }
        '''

    userSearchQuery = '''
        query($name: String) {
            User(name:$name) {
                name
                id
                mediaListOptions {
                    scoreFormat
                }
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
                        count
                        meanScore
                        genres(limit:5, sort:COUNT_DESC) {
                            genre
                        }
                    }
                }
            }
            animeList: MediaListCollection(userName:$name, type:ANIME){
                lists {
                    entries {
                        ...mediaFields
                        media {
                            episodes
                        }
                    }
                }
            }
            mangaList: MediaListCollection(userName:$name, type:MANGA){
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
        }
        fragment mediaFields on MediaList {
            status
            mediaId
            score
            progress
            media {
                bannerImage
                coverImage {
                    large
                }
                title {
                    romaji
                    emglish
                    native
                }
            }
        }
        '''

    mediaQuery = '''
        query(
            $id: Int, 
            $search: String, 
            $asHtml: Boolean, 
            $isManga: Boolean!, 
            $isAnime: Boolean!, 
            $isCharacter: Boolean!, 
            $isMain: Boolean, 
            $format_not_in: [MediaFormat]
        ) {
            manga: Media(id: $id, search: $search, type: MANGA) @include(if: $isManga) {
                ...genericMediaFields
                chapters
            }
            anime: Media(id: $id, search: $search, type: ANIME, format_not_in: $format_not_in) @include(if: $isAnime) {
                ...genericMediaFields
                episodes
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
                english
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
    
    async def aniSearch(session, search, isManga=False, isAnime=False, isCharacter=False):
        """Search anilist for manga, anime, and/or character

        Args:
            session (ClientSession): A session for making post requests. Expected to be from aiohttp.ClientSession()
            search (str): The anilist search string
            isManga (bool): If the results should contain a manga entry
            isAnime (bool): If the results should contain an anime entry
            isCharacter (bool): If the results should contain a character entry
        
        Returns: 
            A valid anilist query response.

        Raises:
            AnilistBadArguments: If valid session or search not supplied
            AnilistError: If valid reponse was not obtained
            AnilistQueryNotResultsError: When the query results in 404 i.e. nothing matched the query
            AnilistDownError: When the response is a 503 i.e. Anilist most likely down
        """
        if not (session and (isManga or isAnime or isCharacter)):
            raise Anilist2.AnilistBadArguments()
            
        v = {
            'search': search,
            'isManga': isManga,
            'isAnime': isAnime,
            'isCharacter': isCharacter,
        }

        if isManga:
            v['asHtml'] = False

        if isAnime:
            v['asHtml'] = False
            v['isMain'] = True
            v['format_not_in'] = ['MANGA', 'NOVEL', 'ONE_SHOT']   

        # async with session.post(Anilist2.apiUrl, json={'query': Anilist2.mediaQuery, 'variables': v}) as resp:
        #     return await Anilist2.__resolveResponse(resp)  
        return await Anilist2.__request(session, Anilist2.mediaQuery, v)       

    
    async def getUserData(session, id):
        """Gets user data from anilist via anilist id

        Args:
            session (ClientSession): A session for making post requests. Expected to be from aiohttp.ClientSession()
            id (int): The anilist id to get data for
        
        Returns: 
            A valid anilist query response.

        Raises:
            AnilistBadArguments: If valid session or name not supplied
            AnilistError: If valid reponse was not obtained
            AnilistQueryNotResultsError: When the query results in 404 i.e. nothing matched the query
            AnilistDownError: When the response is a 503 i.e. Anilist most likely down
        """

        if not (session or id):
            raise Anilist2.AnilistBadArguments()

        return await Anilist2.__request(session, Anilist2.userDataQuery, {'id': id})

        # async with session.post(Anilist2.apiUrl, json={'query': Anilist2.userDataQuery, 'variables': {'id': id}}) as resp:
        #     return await Anilist2.__resolveResponse(resp)


    async def userSearch(session, name):
        """Gets user data from anilist via anilist username

        Args:
            session (aiohttp.ClientSession): A session for making post requests. Expected to be from aiohttp.ClientSession()
            name (str): The anilist username to search with
        
        Returns: 
            A valid anilist query response.

        Raises:
            AnilistBadArguments: If valid session or name not supplied
            AnilistError: If valid reponse was not obtained
            AnilistQueryNotResultsError: When the query results in 404 i.e. nothing matched the query
            AnilistDownError: When the response is a 503 i.e. Anilist most likely down
        """

        if not (session or name):
            raise Anilist2.AnilistBadArguments()

        return await Anilist2.__request(session, Anilist2.userSearchQuery, {'name': name})

        # async with session.post(Anilist2.apiUrl, json={'query': Anilist2.userSearchQuery, 'variables': {'name': name}}) as resp:
        #     return await Anilist2.__resolveResponse(resp)

    
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
            AnilistQueryNotResultsError: When the query results in 404 i.e. nothing matched the query
            AnilistDownError: When the response is a 503 i.e. Anilist most likely down
        """

        if not resp:
            raise Anilist2.AnilistError(000, 'No response')

        if resp.status == 503:
            raise Anilist2.AnilistDownError()

        if resp.status == 404:
            raise Anilist2.AnilistQueryNotResultsError()

        try:
            ret = await resp.json()
        except:
            raise Anilist2.AnilistError('Could not parse json from response')
        else:
            return ret
