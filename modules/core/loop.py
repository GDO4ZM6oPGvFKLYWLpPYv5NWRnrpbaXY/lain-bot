import asyncpg
import discord
from discord.ext import tasks, commands
import time

from modules.config.config import Config
from modules.config.user import User
from modules.anime.anilist import Anilist

class Loop(commands.Cog):

    def __init__(self, bot, al_update_rate):
        self.bot = bot
        self.al_update_rate = al_update_rate
        self.al_update.start()

    def cog_unload(self):
        self.al_update.cancel()

    @tasks.loop(seconds=300.0)
    async def al_update(self):
        print("Checking AL for List Updates")
        for guild in self.bot.guilds:
            if Config.cfgRead(str(guild.id), "alOn") == True:
                channel = guild.get_channel(int(Config.cfgRead(str(guild.id), "alChannel")))
                for member in guild.members:
                    alID = User.userRead(str(member.id), "alID")
                    if alID!=None:
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
                            try:
                                embed.set_image(url=result["media"]["bannerImage"])
                            except:
                                pass

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
                        except:
                            pass
