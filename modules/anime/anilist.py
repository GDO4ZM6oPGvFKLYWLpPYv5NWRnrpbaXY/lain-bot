import graphene
import requests
import json

from modules.core.client import Client

class Anilist(graphene.ObjectType):

	def aniSearch(show):
		# query of info we want from AniList
		query = '''
		query ($id: Int, $search: String, $asHtml: Boolean, $isMain: Boolean, $format_not_in: [MediaFormat]) {
	        Media (id: $id, search: $search, format_not_in: $format_not_in) {
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
	            seasonYear
	            episodes
	            coverImage {
					extraLarge
	            	large
	            }
	            bannerImage
	            genres
	            meanScore
	            popularity
	            studios (isMain: $isMain) {
	            	nodes {
	            		name
	            		siteUrl
	            	}
	            }
	            siteUrl
	        }
		}
		'''

		variables = {
		    'search': show,
		    'asHtml': False,
		    'isMain': True,
			'format_not_in': ['MANGA', 'NOVEL', 'ONE_SHOT']
		}

		source = 'https://graphql.anilist.co'

		response = requests.post(source, json={'query': query, 'variables': variables})
		result = response.json()

		if response.status_code == 200:
			return result
		else:
			print('Anime response code: ' + str(response.status_code) + '\n\n' + str(result))
			return None

	def charSearch(searchID):
		query = '''
			query ($id: Int, $search: String) {
				Character (id: $id, search: $search) {
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
			}
		'''

		variables = {
			'search': searchID
		}

		url = 'https://graphql.anilist.co'

		response = requests.post(url, json={'query': query, 'variables': variables})
		result = response.json()

		if response.status_code == 200:
			return result
		else:
			print('Character response code: ' + str(response.status_code) + '\n\n' + str(result))
			return None

	def userSearch(user):
		#implement query/statistics later
		query = '''
		query ($name: String, $limit: Int, $page: Int, $perPage: Int) {
			User (name: $name) {
				id
				name
				about
				avatar {
					medium
					large
				}
				bannerImage
				options {
					profileColor
				}
				siteUrl
				updatedAt
				statistics {
					anime {
						count
						meanScore
						genres(limit: $limit, sort: COUNT_DESC){
							genre
							count
							meanScore
						}
					}
				}
				favourites{
					anime(page: $page, perPage: $perPage){
						nodes{
							title {
								romaji
								english
							}
						}
					}
				}
			}
		}
		'''

		variables = {
			'name': user,
			'limit': 5,
			'page': 1,
			'perPage': 5
		}

		url = 'https://graphql.anilist.co'

		response = requests.post(url, json={'query': query, 'variables': variables})
		result = response.json()

		if response.status_code == 200:
			return result
		else:
			print('User response code: ' + str(response.status_code) + '\n\n' + str(result))
			return None

	def scoreSearch(user, media):
		#implement query/statistics later
		query = '''
		query ($userId: Int, $mediaId: Int, $format: ScoreFormat) {
			MediaList (userId: $userId, mediaId: $mediaId) {
				mediaId
				score(format:$format)
				status
			}
		}
		'''

		variables = {
			'userId': user,
			'mediaId': media,
			'format': "POINT_10_DECIMAL"
		}

		url = 'https://graphql.anilist.co'

		response = requests.post(url, json={'query': query, 'variables': variables})
		result = response.json()

		if response.status_code == 200:
			return result
		else:
			return None

	def activitySearch(user, time):
		#implement query/statistics later
		query = '''
		query ($userId: Int, $createdAt_greater: Int, $sort: [ActivitySort], $type_in: [ActivityType]) {
			Activity (userId: $userId, createdAt_greater: $createdAt_greater, sort: $sort, type_in: $type_in) {
				... on ListActivity {
					userId
					createdAt
					type
					user {
						name
						avatar {
							large
						}
						options {
							profileColor
						}
					}
					status
					progress
					media {
						type
						title {
							romaji
							english
						}
						bannerImage
						coverImage {
							medium
							extraLarge
						}
						countryOfOrigin
					}
					createdAt
					siteUrl
				}
			}
		}
		'''

		variables = {
			'userId': user,
			'createdAt_greater': time,
			'sort': ["ID_DESC"],
			'type': ["ANIME_LIST", "MANGA_LIST", "MEDIA_LIST"]
		}

		url = 'https://graphql.anilist.co'

		response = requests.post(url, json={'query': query, 'variables': variables})
		result = response.json()

		if response.status_code == 200:
			return result

	# for the user airing show searches
	# input time as 00:00 of the day, 86400
	def watchingSearch(user):
		query = '''
		query ($userId: Int, $status_in: [MediaListStatus], $page: Int, $perPage: Int, $type: MediaType) {
			Page (page: $page, perPage: $perPage){
				mediaList (userId: $userId, status_in: $status_in, type: $type) {
					media {
						id
						siteUrl
						status
						episodes
						bannerImage
						coverImage {
							medium
							extraLarge
						}
						title {
							romaji
							english
						}
						nextAiringEpisode {
						episode
							airingAt
						}
					}
				}
			}
		}
		'''

		variables = {
			'userId': user,
			'status_in': ["CURRENT", "PLANNING"],
			'page': 0,
			'perPage': 50,
			'type': "ANIME"
		}

		url = 'https://graphql.anilist.co'

		response = requests.post(url, json={'query': query, 'variables': variables})
		result = response.json()

		if response.status_code == 200:
			return result
