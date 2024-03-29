import motor.motor_asyncio

class Database:

	def __init__(self, url, name, collection):
		client = motor.motor_asyncio.AsyncIOMotorClient(url)
		self.collection = client[name][collection]

	async def delete_one(self, filter):
		try:
			res = await self.collection.delete_one(filter)
		except:
			return None
		else:
			return res

	async def update_one(self, filter, update, upsert=False):
		try:
			res = await self.collection.update_one(filter, update, upsert)
		except:
			return None
		else:
			return res

	async def update_many(self, filter, update, upsert=False):
		try:
			res = await self.collection.update_many(filter, update, upsert)
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

	def aggregate(self, pipeline=[]):
		return self.collection.aggregate(pipeline)