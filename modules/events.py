import discord
from discord.ext import commands, tasks
import asyncio
import sqlite3
import json
import os
from os import path

from .client import Client
from .config import Config
from .safebooru import Safebooru
from .user import User

bot = Client.bot
game = discord.Game("with her phone") #sets the game the bot is currently playing

class Events:

	@bot.event
	async def on_ready(): #bot startup event

		print('Kotori-san is ready to go!')
		await bot.change_presence(status=discord.Status.online, activity=game)

		# channel = bot.get_channel(Config.botChannel)
		# Client.serverID = channel.guild.id

		# safebooruSearch = Safebooru.booruSearch('otonashi_kotori 1girl')

#
		# safebooruImageURL = safebooruSearch[0]
		# safebooruPageURL = safebooruSearch[1]
		# safebooruTagsTogether = safebooruSearch[2]

#
		# embed = discord.Embed(
			# title = 'こんにちは、プロデューサーさん！',
			# description = 'Kotori is now online!',
			# color = discord.Color.green(),
			# url = safebooruPageURL
		# )

#
		# embed.set_image(url=safebooruImageURL)
		# embed.set_author(name='音無小鳥', url='https://www.project-imas.com/wiki/Kotori_Otonashi', icon_url='https://raw.githubusercontent.com/SigSigSigurd/kotori-san-bot/master/assets/search.png')
		# embed.set_footer(text=safebooruTagsTogether)

#

		# writes initial config files for each server the bot is in, and updates the dictionary with the current server name
		for guild in bot.guilds:
			serverID = str(guild.id)
			serverName = str(guild.name)
			if path.exists(os.getcwd()+"/config/"+serverID+".json"):
				Config.cfgUpdate(serverID, "Name", serverName)
			else:
				with open(os.getcwd()+"/config/"+serverID+".json", "x") as server_json:
					json_data = {"Name": serverName}
					json.dump(json_data, server_json)
		for user in bot.users:
			userID = str(user.id)
			userName = str(user.name)
			if path.exists(os.getcwd()+"/user/"+userID+".json"):
				User.userUpdate(userID, "Name", userName)
			else:
				with open(os.getcwd()+"/user/"+userID+".json", "x") as user_json:
					json_data = {"Name": userName}
					json.dump(json_data, user_json)

	@bot.event
	async def on_member_join(member):
		if str(member) == 'UWMadisonRecWell#3245':
			for guild in bot.guilds:
				if str(guild.id) == '554770485079179264':
					role = discord.utils.get(guild.roles, name='RecWell')
					await discord.Member.add_roles(member, role)
					break
