import discord
from discord.ext import commands

# from modules.cogs.anime import Anime
from modules.cogs.music import Music
from modules.cogs.fighting import Fighting
from modules.cogs.configuration import Configuration
from modules.cogs.memes import Memes
from modules.cogs.animeclub import AnimeClub
from modules.cogs.jisho import Jisho

intents = discord.Intents.none()
intents.guilds = True
intents.guild_messages = True
intents.guild_reactions = True
intents.members = True
intents.voice_states = True

prefix = ">"

class Client:	
    bot = commands.Bot(command_prefix=prefix, intents=intents) #sets up the bot

    bot.add_cog(Memes(bot))
    bot.add_cog(Fighting(bot))
    # bot.add_cog(Anime(bot))
    bot.add_cog(Configuration(bot))
    bot.add_cog(Music(bot))
    bot.add_cog(AnimeClub(bot))
    bot.add_cog(Jisho(bot))