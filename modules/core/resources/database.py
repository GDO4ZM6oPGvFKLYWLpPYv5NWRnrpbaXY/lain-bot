import motor.motor_asyncio

class Database:

	def __init__(self, url, name, collection):
		client = motor.motor_asyncio.AsyncIOMotorClient(url)
		self.collection = client[name][collection]

	async def update_one(self, filter, update, upsert=False):
		try:
			res = await self.collection.update_one(filter, update, upsert)
		except:
			return None
		else:
			return res

	async def find_one(self, filter, projection=None):
		try:
			res = await self.collection.find_one(filter, projection)
		except:
			return None
		else:
			return res

	def find(self, filter={}, projection=None):
		return self.collection.find(filter, projection)