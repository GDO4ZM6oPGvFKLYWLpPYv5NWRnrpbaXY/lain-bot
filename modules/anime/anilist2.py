class Anilist2:

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
            mangaList: MediaListCollection(userName:$name, type:MANGA){
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
        if not (session and (isManga or isAnime or isCharacter)):
            return None
            
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

        async with session.post(Anilist2.apiUrl, json={'query': Anilist2.mediaQuery, 'variables': v}) as resp:
            return await Anilist2.__resolveResponse(resp)         

    
    async def getUserData(session, id):
        """Gets user data from anilist via anilist id

        Args:
            session (ClientSession): A session for making post requests. Expected to be from aiohttp.ClientSession()
            id (int): The anilist id to get data for
        
        Returns: 
            A valid anilist query response. Otherwise, None
        """

        if not (session or id):
            return None

        async with session.post(Anilist2.apiUrl, json={'query': Anilist2.userDataQuery, 'variables': {'id': id}}) as resp:
            return await Anilist2.__resolveResponse(resp)


    async def userSearch(session, name):
        """Gets user data from anilist via anilist username

        Args:
            session (aiohttp.ClientSession): A session for making post requests. Expected to be from aiohttp.ClientSession()
            name (str): The anilist username to search with
        
        Returns: 
            A valid anilist query response. Otherwise, None
        """

        if not (session or name):
            return None

        async with session.post(Anilist2.apiUrl, json={'query': Anilist2.userSearchQuery, 'variables': {'name': name}}) as resp:
            return await Anilist2.__resolveResponse(resp)
    

    async def __resolveResponse(resp):
        """Tries to resolve response into well-formatted json derived dictionary. 
        Response errors will be reformatted into anilist's standard query errors object (https://anilist.gitbook.io/anilist-apiv2-docs/overview/graphql/errors).

        Args:
            resp (aiohttp.ClientResponse): The response to resolve

        Returns:
            A valid json response as dictionary. Otherwise, None

        Raises:
            ClientResponseError: If http response code is >=400
        """

        if not resp:
            return None

        if resp.status != 200:
            return {
                'data': None,
                'errors': [
                    {
                        'message': resp.reason,
                        'status': resp.status
                    }
                ]
            }

        try:
            ret = await resp.json()
        except:
            return None
        else:
            return ret
