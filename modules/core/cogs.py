import discord
from discord.ext import commands
import time
import os

import json

from modules.core.loop import Loop
from modules.core.client import Client

from modules.commands.anime import Anime
from modules.commands.music import Music
from modules.commands.fighting import Fighting
from modules.commands.configuration import Configuration
from modules.commands.memes import Memes

bot = Client.bot

class Cogs:
    bot.add_cog(Memes(bot))
    bot.add_cog(Fighting(bot))
    bot.add_cog(Anime(bot))
    bot.add_cog(Configuration(bot))
    bot.add_cog(Music(bot))

    bot.add_cog(Loop(bot, 150, Anime.al_json))
