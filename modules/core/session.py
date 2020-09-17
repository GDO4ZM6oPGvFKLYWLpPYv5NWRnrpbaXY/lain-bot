from discord.ext import commands
import aiohttp, asyncio

class Session(commands.Cog):

	def __init__(self, bot):
		self.bot = bot
		self.session = aiohttp.ClientSession()

	async def close_session(self):
		await self.session.close()

	def cog_unload(self):
		tmp_loop = asyncio.new_event_loop()
		tmp_loop.run_until_complete(self.close_session(self))
		tmp_loop.close()
