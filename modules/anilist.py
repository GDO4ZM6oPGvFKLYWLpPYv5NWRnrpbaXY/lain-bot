import graphene
import requests
import json

class Anilist(graphene.ObjectType):

	def aniSearch(searchID):
		query = '''
		query ($id: Int) { # Define which variables will be used in the query (id)
			Media (id: $id, type: ANIME) {
				id
				title {
					romaji
					english
					native
				}
			}
		}
		'''

		variables = {
			'id': searchID
		}

		url = 'https://graphql.anilist.co'

		response = requests.post(url, json={'query': query, 'variables': variables})

		return response
