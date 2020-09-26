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
            if resp.status != 200:
                return None
            
            return await Anilist2.getJsonFromResp(resp)


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
            if resp.status != 200:
                return None
                
            return await Anilist2.getJsonFromResp(resp)
    

    async def getJsonFromResp(resp):
        """Tries to retrieve valid json from response

        Args:
            resp (aiohttp.ClientResponse): The response to get json from

        Returns:
            A valid json response. Otherwise, None
        """

        try:
            ret = await resp.json()
        except:
            return None
        else:
            return ret
