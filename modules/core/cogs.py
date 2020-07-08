import discord
from discord.ext import commands
import time

from modules.core.loop import Loop
from modules.core.client import Client
from modules.core.events import Events

from modules.commands.anime import Anime
from modules.commands.music import Music
from modules.commands.fighting import Fighting
from modules.commands.configuration import Configuration
from modules.commands.memes import Memes

bot = Client.bot
al_json = Events.al_json
class Cogs:
    bot.add_cog(Memes(bot))
    bot.add_cog(Fighting(bot))
    bot.add_cog(Anime(bot))
    bot.add_cog(Configuration(bot))
    bot.add_cog(Music(bot))

    bot.add_cog(Loop(bot, 300, al_json))
