import aiohttp, asyncio, sys

class SessionSetException(Exception):
	def __init__(self, message="Session can only be set upon instantiation"):
		self.message = message
		super().__init__(self.message)

class Session(aiohttp.ClientSession):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	async def __close_session_exec(self):
		await self.close()
		await asyncio.sleep(0.1)

	def close_session(self):
		loop = asyncio.get_event_loop()
		if loop.is_closed():
			# https://github.com/encode/httpx/issues/914
			# graceful shutdown on recent python and windows
			if sys.version_info[0] == 3 and sys.version_info[1] >= 8 and sys.platform.startswith('win'):
				asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
			loop = asyncio.new_event_loop()
			asyncio.set_event_loop(loop)
			loop.run_until_complete(self.__close_session_exec())
			asyncio.set_event_loop_policy(None) # go back to default policy
		else:
			asyncio.ensure_future(self.__close_session_exec())
