import discord
from discord.ext import commands
import time
import json
import os

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

    al_json = json.load(open(os.getcwd()+"/modules/anime/config/alID.json", 'r'))

    bot.add_cog(Loop(bot, 300, al_json))
