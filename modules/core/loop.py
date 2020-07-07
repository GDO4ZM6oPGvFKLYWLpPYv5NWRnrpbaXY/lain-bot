from discord.ext import tasks, commands

from modules.core.client import Client

bot = Client.bot
class Loop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.al_update.start()

    def cog_unload(self):
        self.al_update.cancel()

    @tasks.loop(seconds=5.0)
    async def al_update(self):
        print(self.index)
        self.index+=1
