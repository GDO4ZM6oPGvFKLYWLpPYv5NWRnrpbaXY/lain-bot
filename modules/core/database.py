import motor.motor_asyncio, os, logging
logger = logging.getLogger(__name__)

class Database:
	if not bool(os.getenv('NON_SRV_DB', default=False)):
		client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://'+os.getenv('DBUSER')+':'+os.getenv('DBKEY')+'@' + os.getenv('DBPATH'))
	else:
		client = motor.motor_asyncio.AsyncIOMotorClient('mongodb://'+os.getenv('DBUSER')+':'+os.getenv('DBKEY')+'@' + os.getenv('DBPATH'))


	"""
	user model:
		_id				mongodb generated id
		discordId		str - discord id for user
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
		animeMessageChannels	[str] - channel ids where anime messages are enabled
		mangaMessageChannels	[str] - channel ids where manga messages are enabled
		r18Enabled				bool - bool to toggle whether or not hentai are enabled in manga channels
		name					str - name of guild (not really needed, just there for debugging)
	"""
	# Tatsu - I'd make a r18 channel thing but I suck at coding and don't care enough

	def guildCollection():
		return Database.client['lain-bot']['guilds']

	"""
	storage model:
		_id						mongodb generated id
		id						str - string to name storage item
	"""
	def storageCollection():
		return Database.client['lain-bot']['storage']


	async def user_update_one(filter, update, upsert=False):
		"""Update a user in db

			Args:
				filter (obj): A query that matches the user to update
				update (obj): The modifications to apply
				upsert (bool, optional): If True, insert document if filter found no matches. Defaults to False.

			Returns:
				UpdateResult or None: On success, return info pertaining to update, otherwise, None
		"""

		try:
			res = await Database.userCollection().update_one(filter, update, upsert)
		except:
			return None
		else:
			return res


	def user_find(filter, projection=None):
		"""Find a users in db

			Args:
				filter (obj): A query that matches the users to find
				projection (obj, optional): MongoDB projection. Defaults to no projection.

			Returns:
				MotorCursor: A cursor
		"""

		try:
			res = Database.userCollection().find(filter, projection)
		except:
			return None
		else:
			return res


	async def user_find_one(filter, projection=None):
		"""Find a user in db

			Args:
				filter (obj): A query that matches the user to find
				projection (obj, optional): MongoDB projection. Defaults to no projection.

			Returns:
				document or None: The found document or None
		"""

		try:
			res = await Database.userCollection().find_one(filter, projection)
		except:
			return None
		else:
			return res


	async def guild_update_one(filter, update, upsert=False):
		"""Update a guild in db

			Args:
				filter (obj): A query that matches the guild to update
				update (obj): The modifications to apply
				upsert (bool, optional): If True, insert document if filter found no matches. Defaults to False.

			Returns:
				UpdateResult or None: On success, return info pertaining to update, otherwise, None
		"""

		try:
			res = await Database.guildCollection().update_one(filter, update, upsert)
		except:
			return None
		else:
			return res


	def guild_find(filter, projection=None):
		"""Find a guilds in db

			Args:
				filter (obj): A query that matches the guilds to find
				projection (obj, optional): MongoDB projection. Defaults to no projection.

			Returns:
				MotorCursor: A cursor
		"""

		try:
			res = Database.guildCollection().find(filter, projection)
		except:
			return None
		else:
			return res


	async def guild_find_one(filter, projection=None):
		"""Find a guild in db

			Args:
				filter (obj): A query that matches the guild to find
				projection (obj, optional): MongoDB projection. Defaults to no projection.

			Returns:
				document or None: The found document or None
		"""

		try:
			res = await Database.guildCollection().find_one(filter, projection)
		except:
			return None
		else:
			return res


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


	def userScoreFormat(user, fetched_user=None):
		"""Get a user's score format as string i.e. their denominator for scoring

			Args:
				user (obj): The user to get the score format from
				fetched_user (obj)[optional]: The fetched anilist user to get the score
					format from. Optional, will just get format from user if
					not provided

			Returns:
				str: The scoring format. Will return 'XX' if any trouble and
				'CHNG' if format differs between fetched_user and user
		"""

		try:
			fmt = user['profile']['mediaListOptions']['scoreFormat']
			if fetched_user and fmt != fetched_user['data']['User']['mediaListOptions']['scoreFormat']:
				return 'CHNG'
		except:
			return 'XX'
		else:
			if fmt == 'POINT_100':
				return '100'
			elif fmt == 'POINT_10_DECIMAL':
				return '10.0'
			elif fmt == 'POINT_10':
				return '10'
			elif fmt == 'POINT_5':
				return '5'
			else:
				return '3'

	def scoreFormated(score, fmt):
		"""Get formated score based on user's score format. e.g. 9.2/10, 5/5, etc

			Args:
				score (float, str): The score to be formated
				fmt (str): The score format to use

			Returns:
				str: The fully formated score. Will return 'XX' if any trouble
		"""
		if fmt in ['XX', 'CHNG']:
			return 'XX'

		score = str(score)

		if fmt != '3':
			if score == '0':
				return '-/' + fmt
			else:
				return str(score) + '/' + fmt
		else:
			if score == '0':
				return '-'
			elif score == '1':
				return '🙁'
			elif score == '2':
				return '😐'
			elif score == '3':
				return '🙂'
			else:
				return 'XX'


	async def storage_update_one(filter, update):
		"""Update something in storage

			Args:
				filter (obj): A query that matches the storage item to update
				update (obj): The modifications to apply

			Returns:
				UpdateResult or None: On success, return info pertaining to update, otherwise, None
		"""

		try:
			res = await Database.storageCollection().update_one(filter, update)
		except:
			logger.warning('Exception finding storage item in db.',
				exc_info=True)
			return None
		else:
			return res


	async def storage_find_one(filter, projection=None):
		"""Find a storage item in db

			Args:
				filter (obj): A query that matches the storage item to find
				projection (obj, optional): MongoDB projection. Defaults to no projection.

			Returns:
				document or None: The found document or None
		"""

		try:
			res = await Database.storageCollection().find_one(filter, projection)
		except:
			logger.warning('Exception finding storage item in db.',
				exc_info=True)
			return None
		else:
			return res
