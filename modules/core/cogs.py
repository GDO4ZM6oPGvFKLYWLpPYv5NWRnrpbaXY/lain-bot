import discord
from discord.ext import commands
import time
import os

import json

from modules.core.loop import Loop
from modules.core.client import Client

from modules.cogs.anime import Anime
from modules.cogs.music import Music
from modules.cogs.fighting import Fighting
from modules.cogs.configuration import Configuration
from modules.cogs.memes import Memes
from modules.cogs.testing import Testing

from modules.esports.esportsclub import EsportsClub

bot = Client.bot

class Cogs:
    bot.add_cog(Memes(bot))
    bot.add_cog(Fighting(bot))
    bot.add_cog(Anime(bot))
    bot.add_cog(Configuration(bot))
    bot.add_cog(Music(bot))
    bot.add_cog(Testing(bot))

    #temporary?
    bot.add_cog(EsportsClub(bot))

    bot.add_cog(Loop(bot, Anime.al_json))
