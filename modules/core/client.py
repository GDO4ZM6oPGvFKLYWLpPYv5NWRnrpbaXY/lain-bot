import discord, asyncio
from discord.ext import commands

from modules.cogs.weeb import Weeb
from modules.cogs.music import Music
from modules.cogs.configuration import Configuration
from modules.cogs.memes import Memes
from modules.cogs.animeclub import AnimeClub
from modules.cogs.jisho import Jisho
from modules.cogs.daijoubu import Daijoubu
from modules.cogs.songs import Songs
from modules.cogs.misc import Misc
from modules.cogs.user import User

from modules.services import Service
from modules.core.resources import Resources

intents = discord.Intents.none()
intents.guilds = True
intents.guild_messages = True
intents.guild_reactions = True
intents.members = True
intents.voice_states = True
intents.message_content = True

prefix = ">"

class CustomHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        e = discord.Embed(color=16711680, description='')
        for page in self.paginator.pages:
            e.description += page
        await destination.send(embed=e)

class Bot(commands.Bot):
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    async def setup_hook(self):
        await Resources.init()

        await Service.register(self)

        await asyncio.gather(*[
            self.add_cog(Memes(self)),
            self.add_cog(Weeb(self)),
            self.add_cog(Configuration(self)),
            self.add_cog(Music(self)),
            self.add_cog(Songs(self)),
            self.add_cog(AnimeClub(self)),
            self.add_cog(Jisho(self)),
            self.add_cog(Daijoubu(self)),
            self.add_cog(Misc(self)),
            self.add_cog(User(self)),
        ])

        self.help_command = CustomHelpCommand()
    

class Client:	
    bot = Bot(command_prefix=prefix, intents=intents) #sets up the bot
