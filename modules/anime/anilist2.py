import aiohttp

from modules.core.session import Session

class Anilist2:

    apiUrl = 'https://graphql.anilist.co'

    userDataQuery = '''
        query($id: Int) {
            User(id:$id) {
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
                updatedAt
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
                updatedAt
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

# TODO error checks
    async def getUserData(session, id):
        async with session.post(Anilist2.apiUrl, json={'query': Anilist2.userDataQuery, 'variables': {'id': id}}) as resp:
            return await resp.json()

    async def userSearch(session, name):
        if not name:
            return
        async with session.post(Anilist2.apiUrl, json={'query': Anilist2.userSearchQuery, 'variables': {'name': name}}) as resp:
            return await resp.json()
