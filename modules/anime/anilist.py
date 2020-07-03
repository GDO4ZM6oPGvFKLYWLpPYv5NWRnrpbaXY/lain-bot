import graphene
import requests
import json

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