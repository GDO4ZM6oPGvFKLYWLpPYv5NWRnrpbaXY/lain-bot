import discord
from discord.ext import commands

from modules.cogs.anime import Anime
from modules.cogs.music import Music
from modules.cogs.configuration import Configuration
from modules.cogs.memes import Memes
from modules.cogs.animeclub import AnimeClub
from modules.cogs.jisho import Jisho
from modules.cogs.daijoubu import Daijoubu

from modules.services import Service

intents = discord.Intents.none()
intents.guilds = True
intents.guild_messages = True
intents.guild_reactions = True
intents.members = True
intents.voice_states = True

prefix = ">"

class CustomHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        e = discord.Embed(color=16711680, description='')
        for page in self.paginator.pages:
            e.description += page
        await destination.send(embed=e)

class Client:	
    bot = commands.Bot(command_prefix=prefix, intents=intents) #sets up the bot

    Service.register(bot)

    bot.add_cog(Memes(bot))
    bot.add_cog(Anime(bot))
    bot.add_cog(Configuration(bot))
    bot.add_cog(Music(bot))
    bot.add_cog(AnimeClub(bot))
    bot.add_cog(Jisho(bot))
    bot.add_cog(Daijoubu(bot))

    bot.help_command = CustomHelpCommand()
