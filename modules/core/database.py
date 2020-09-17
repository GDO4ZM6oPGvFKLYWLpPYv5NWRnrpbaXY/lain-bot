import motor.motor_asyncio, os

class Database:
	client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://'+os.getenv('DBUSER')+':'+os.getenv('DBKEY')+'@cluster0.n52hk.gcp.mongodb.net/lain-bot?retryWrites=true&w=majority')

	"""
	user model:
		_id				mongodb generated id
		discordId		int - discord id for user
		anilistId		int - anilist id
		anilistName		str - anilist name
		profile			{} - anilist profile data (genres, favs, etc)
		animeList		{} - anilist animelist
		mangaList		{} - anilist mangalist
		status			int: 0=disabled(removed), 1=enabled(set)
	"""
	def userCollection():
		return Database.client['lain-bot']['users']
	
	"""
	guild model:
		_id						mongodb generated id	
		id						int - discord id for guild
		animeMessageChannels	[int] - channel ids where anime messages are enabled
		mangaMessageChannels	[int] - channel ids where manga messages are enabled
		name					str - name of guild (not really needed, just there for debugging)
	"""
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