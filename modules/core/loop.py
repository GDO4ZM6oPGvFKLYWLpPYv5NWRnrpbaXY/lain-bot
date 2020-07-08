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

    def __init__(self, bot, al_update_rate, al_json):
        self.bot = bot
        self.al_update_rate = al_update_rate
        self.al_json = al_json
        self.al_update.start()

    def cog_unload(self):
        self.al_update.cancel()



    @tasks.loop(seconds=300.0)
    async def al_update(self):
        print("Checking AL for List Updates")

        print("Loaded AL JSON")
        for guild in self.bot.guilds:
            if Config.cfgRead(str(guild.id), "alOn") == True:
                channel = guild.get_channel(int(Config.cfgRead(str(guild.id), "alChannel")))
                for member in guild.members:
                    #alID = User.userRead(str(member.id), "alID")
                    if self.al_json[str(member.id)]!=0 or None:
                        alID = self.al_json[str(member.id)]
                        print(alID)
                        timeInt = int(time.time())
                        try:
                            result = Anilist.activitySearch(alID, timeInt-self.al_update_rate)["data"]["Activity"]
                        except:
                            result = None

                        try:
                            embed = discord.Embed(
                                title = str(member.name),
                                url = result["siteUrl"]
                            )
                            if result["media"]["bannerImage"]!=0 or None:
                                embed.set_image(url=result["media"]["bannerImage"])

                            embed.set_footer(text="Posted at: "+str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result["createdAt"]))))
                            if result["status"] == "watched episode":
                                embed.add_field(name="Updated their list on AniList: ", value=str(result["status"]).capitalize()+" "+str(result["progress"])+" of "+result["media"]["title"]["romaji"], inline=True)
                            else:
                                embed.add_field(name="Updated their list on AniList: ", value=str(result["status"]).capitalize()+" "+result["media"]["title"]["romaji"], inline=True)
                            try:
                                await channel.send(embed=embed)
                                print("Posting list updates of "+member.name)
                            except:
                                pass
                        except Exception as e:
                            pass
        print("Successfully updated lists on AL!")
