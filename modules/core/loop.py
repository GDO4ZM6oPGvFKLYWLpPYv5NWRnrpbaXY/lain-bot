import asyncpg
import discord
from discord.ext import tasks, commands
import time
import os
import json

from datetime import datetime, timezone, timedelta

from modules.config.config import Config
from modules.config.user import User
from modules.anime.anilist import Anilist

class Loop(commands.Cog):



    def __init__(self, bot, al_json):
        self.bot = bot
        self.al_json = al_json
        self.al_update.start()
        self.al_timer.start()
        #self.al_airing.start()
        self.update_count=0

    def cog_unload(self):
        self.al_update.cancel()

    # loop for updating user AniList; optimize later
    # Later make sure to implement some method for catching 'missed' updates
    @tasks.loop(seconds=10.0)
    async def al_update(self):
        if self.update_count<60:
            for guild in self.bot.guilds:
                if Config.cfgRead(str(guild.id), "alAnimeOn") == True or Config.cfgRead(str(guild.id), "alMangaOn"):
                    animeChannel = guild.get_channel(int(Config.cfgRead(str(guild.id), "alAnimeChannel")))
                    mangaChannel = guild.get_channel(int(Config.cfgRead(str(guild.id), "alMangaChannel")))
                    for member in guild.members:
                        #alID = User.userRead(str(member.id), "alID")
                        if str(member.id) in self.al_json:
                            alID = self.al_json[str(member.id)]
                            # print(time.strftime("[%H:%M", time.gmtime())+"] Checking user "+member.name+" (AL ID:"+str(alID)+") for list updates.")
                            timeInt = int(time.time())
                            result = Anilist.activitySearch(alID, timeInt-10.0)
                            # print(result)
                            if result != None:
                                self.update_count = self.update_count+1
                                result = result["data"]["Activity"]
                                # later i'll implement a command that toggles this filter
                                if result["media"]["countryOfOrigin"]=="JP":
                                    try:
                                        embed = discord.Embed(
                                            title = str(member.name),
                                            url = result["siteUrl"]
                                        )
                                        #custom random banners in next update
                                        if result["media"]["bannerImage"]!=None:
                                            embed.set_image(url=result["media"]["bannerImage"])
                                        elif result["media"]["coverImage"]["extraLarge"]!=None:
                                            embed.set_image(url=result["media"]["coverImage"]["extraLarge"])
                                        elif result["media"]["coverImage"]["medium"]!=None:
                                            embed.set_image(url=result["media"]["coverImage"]["medium"])

                                        embed.set_footer(text="Posted at: "+str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result["createdAt"]))))

                                        if result["status"] == "watched episode" or result["status"] == "read chapter":
                                            embed.add_field(name="Updated their list on AniList: ", value=str(result["status"]).capitalize()+" "+str(result["progress"])+" of "+result["media"]["title"]["romaji"], inline=True)
                                        else:
                                            embed.add_field(name="Updated their list on AniList: ", value=str(result["status"]).capitalize()+" "+result["media"]["title"]["romaji"], inline=True)
                                        try:
                                            if result["media"]["type"] == "ANIME":
                                                await animeChannel.send(embed=embed)
                                            if result["media"]["type"] == "MANGA":
                                                await mangaChannel.send(embed=embed)
                                            print(time.strftime("[%H:%M", time.gmtime())+"] Posting list updates of "+str(member.name))
                                        except Exception as e:
                                            print("Exception with posting embed!")
                                            print(e)
                                    except Exception as e:
                                        print("Exception with something else!")
                                        print(e)
        # print(time.strftime("[%H:%M", time.gmtime())+"] Successfully checked AL for list updates!")

    @tasks.loop(seconds=60.0)
    async def al_timer(self):
        if self.update_count>0:
            print(time.strftime("[%H:%M", time.gmtime())+"] Resetting anime update count.")
            self.update_count=0

    @tasks.loop(seconds=900)
    async def al_airing(self):
        if self.update_count<60:
            for guild in self.bot.guilds:
                if Config.cfgRead(str(guild.id), "alAnimeOn"):
                    channel = guild.get_channel(int(Config.cfgRead(str(guild.id), "alAnimeChannel")))
                    shows = {}
                    timeInt = int(time.time())
                    for member in guild.members:
                        if str(member.id) in self.al_json:
                            alID = self.al_json[str(member.id)]
                            result = Anilist.watchingSearch(alID)
                            if result != None:
                                self.update_count=self.update_count+1
                                result = result["data"]["Page"]["mediaList"]
                                for res in result:
                                    r = res["media"]
                                    if r["status"] == "RELEASING" and r["episodes"]<51:
                                        id = r["id"]
                                        shows[id] = r
                                        # gets rid of duplicate results

                    for show, v in shows.items():
                        airtime = v["nextAiringEpisode"]["airingAt"]
                        if airtime-timeInt < 900:
                            try:
                                embed = discord.Embed(
                                    title = v["title"]["romaji"],
                                    url = v["siteUrl"]
                                )
                                if v["bannerImage"]!=None:
                                    embed.set_image(url=v["bannerImage"])
                                elif v["coverImage"]["extraLarge"]!=None:
                                    embed.set_image(url=v["coverImage"]["extraLarge"])
                                elif v["coverImage"]["medium"]!=None:
                                    embed.set_image(url=v["coverImage"]["medium"])

                                # set to CST right now
                                localTime = airtime - 18000

                                embed.add_field(name="Episode "+str(v["nextAiringEpisode"]["episode"])+" releasing soon", value="Airing at "+time.strftime('%I:%M %p', time.gmtime(localTime))+" (CST)", inline=True)

                                await channel.send(embed=embed)
                            except Exception as e:
                                print(e)
