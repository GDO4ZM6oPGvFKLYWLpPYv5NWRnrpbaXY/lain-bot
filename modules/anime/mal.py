import requests
import json

class Mal():

	def aniSearch(show):
		
        # authentication token
		headers = {
			'Authorization': 'Bearer ' + json.load(open('mal.json', 'r'))['token']
		}

		print(show)

		# search term and limit results
		params = (
			('q', str(show)),
			('limit', '10')
		)

		# get search result
		response = requests.get('https://api.myanimelist.net/v2/anime', headers=headers, params=params).json()

		# if nothing valid returned use next option
		try:
			result = str(response['data'][0]['node']['id'])
		except:
			print('paging')
			response = requests.get(response['paging']['next'], headers=headers, params=params).json()
			result = str(response['data'][0]['node']['id'])


		# request extra info about show
		params = (
			('fields', 'id,title,main_picture,start_date,end_date,synopsis,mean,rank,popularity,num_list_users,num_scoring_users,nsfw,created_at,updated_at,media_type,status,genres,my_list_status,num_episodes,start_season,broadcast,source,average_episode_duration,rating,pictures,background,related_anime,related_manga,recommendations,studios,statistics'),
		)

		response = requests.get('https://api.myanimelist.net/v2/anime/' + result, headers=headers, params=params).json()

		return response