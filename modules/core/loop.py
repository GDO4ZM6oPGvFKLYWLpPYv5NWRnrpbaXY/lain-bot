import asyncpg
import discord
from discord.ext import tasks, commands
import time
import os
import json

from modules.config.config import Config
from modules.config.user import User
from modules.anime.anilist import Anilist

class Loop(commands.Cog):

    def __init__(self, bot, al_json):
        self.bot = bot
        self.al_json = al_json
        self.al_update.start()

    def cog_unload(self):
        self.al_update.cancel()

    # loop for updating user AniList; optimize later
    @tasks.loop(seconds=150.0)
    async def al_update(self):
        print(time.strftime("[%H:%M", time.gmtime())+"] Checking AL for List Updates")
        for guild in self.bot.guilds:
            if Config.cfgRead(str(guild.id), "alOn") == True:
                channel = guild.get_channel(int(Config.cfgRead(str(guild.id), "alChannel")))
                for member in guild.members:
                    #alID = User.userRead(str(member.id), "alID")
                    try:
                        if self.al_json[str(member.id)]!=0 or None:
                            alID = self.al_json[str(member.id)]
                            print(time.strftime("[%H:%M", time.gmtime())+"] Checking user "+member.name+" ("+str(alID)+") for list updates.")
                            timeInt = int(time.time())
                            result = Anilist.activitySearch(alID, timeInt-150.0)["data"]["Activity"]
                            if result != None:
                                print(result)

                            try:
                                embed = discord.Embed(
                                    title = str(member.name),
                                    url = result["siteUrl"]
                                )

                                #custom random banners in next update
                                if result["media"]["bannerImage"]!=None:
                                    embed.set_image(url=result["media"]["bannerImage"])

                                embed.set_footer(text="Posted at: "+str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result["createdAt"]))))
                                if result["status"] == "watched episode":
                                    embed.add_field(name="Updated their list on AniList: ", value=str(result["status"]).capitalize()+" "+str(result["progress"])+" of "+result["media"]["title"]["romaji"], inline=True)
                                else:
                                    embed.add_field(name="Updated their list on AniList: ", value=str(result["status"]).capitalize()+" "+result["media"]["title"]["romaji"], inline=True)
                                try:
                                    await channel.send(embed=embed)
                                    print(time.strftime("[%H:%M", time.gmtime())+"] Posting list updates of "+member.name)
                                except Exception as e:
                                    print(e)
                            except Exception as e:
                                print(e)
                    except Exception as e:
                        print(e)
        print(time.strftime("[%H:%M", time.gmtime())+"] Successfully check AL for list updates!")
