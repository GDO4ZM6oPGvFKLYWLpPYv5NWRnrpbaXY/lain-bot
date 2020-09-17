import motor.motor_asyncio, os

class Database:
	client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://'+os.getenv('DBUSER')+':'+os.getenv('DBKEY')+'@cluster0.n52hk.gcp.mongodb.net/lain-bot?retryWrites=true&w=majority')

	def userCollection():
		return Database.client['lain-bot']['users']

	def guildCollection():
		return Database.client['lain-bot']['guilds']

	# returns None for bad arguments or not found
	async def getUserData(anilistId=None, discordId=None):
		if anilistId is None and discordId is None:
			return None
		d = Database.client['lain-bot']['users']
		if anilistId is not None:
			return await d.find_one({'anilistId':anilistId})
		else:
			return await d.find_one({'discordId':discordId})

	# type either 'anime' or 'manga'
	def formListEntryFromAnilistEntry(anilistEntry, anime=True):
		new_entry = {
			'status': anilistEntry['status'],
			'score': anilistEntry['score'],
			'progress': anilistEntry['progress'],
			'title': anilistEntry['media']['title']['romaji']
		}

		if anime:
			new_entry['episodes'] =  anilistEntry['media']['episodes']
		else:
			new_entry['progressVolumes'] = anilistEntry['progressVolumes']
			new_entry['chapters'] = anilistEntry['media']['chapters']
			new_entry['volumes'] = anilistEntry['media']['volumes']
		
		return new_entry