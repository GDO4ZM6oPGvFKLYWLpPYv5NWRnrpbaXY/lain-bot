import discord
from discord.ext import commands
import os
import dotenv
import json
import time

from modules.anime.anilist import Anilist
from modules.core.client import Client

class Testing(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def test(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid test command passed...')

    @test.command(pass_context=True)
    async def updates(self, ctx):
        member = ctx.message.author
        al_json_path = os.getenv("OS_PATH")+"/modules/anime/config/alID.json"
        al_json = json.load(open(al_json_path, 'r'))
        if al_json[str(member.id)]!=0 or None:
            alID = al_json[str(member.id)]
            result = Anilist.activitySearch(alID, int(time.time())-150)
            if result!=None:
                result = result["data"]["Activity"]
            print(result)
        try:
            await ctx.send(str(result))
        except Exception as e:
            print(e)
            await ctx.send("None!")
