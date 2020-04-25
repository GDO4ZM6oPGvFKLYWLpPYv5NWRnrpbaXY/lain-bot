import discord
from discord.ext import commands, tasks
import asyncio
import sqlite3

from .client import Client
from .config import Config
from .safebooru import Safebooru

bot = Client.bot
game = discord.Game("with her phone") #sets the game the bot is currently playing

class Events:
	
	@bot.event
	async def on_ready(): #bot startup event
		print('Kotori-san is ready to go!')
		await bot.change_presence(status=discord.Status.online, activity=game)
		
		channel = bot.get_channel(Config.botChannel)
		Client.serverID = channel.guild.id
		
		safebooruSearch = Safebooru.booruSearch('otonashi_kotori 1girl')
		
		safebooruImageURL = safebooruSearch[0]
		safebooruPageURL = safebooruSearch[1]
		safebooruTagsTogether = safebooruSearch[2]
		
		embed = discord.Embed(
			title = 'こんにちは、プロデューサーさん！',
			description = 'Kotori is now online!',
			color = discord.Color.green(),
			url = safebooruPageURL
		)
		
		embed.set_image(url=safebooruImageURL)
		embed.set_author(name='音無小鳥', url='https://www.project-imas.com/wiki/Kotori_Otonashi', icon_url='https://raw.githubusercontent.com/SigSigSigurd/kotori-san-bot/master/assets/search.png')
		embed.set_footer(text=safebooruTagsTogether)
			
		#await channel.send(embed=embed)
			
	# def updateDB():
		# #t = Client.serverID
		# t = 400
		
		# conn = sqlite3.connect('db/config.db') #connects to the config database
		# c = conn.cursor()
		
		# print('Test3')
	
		# c.execute('Select * FROM servers WHERE serverID=?', t)
		# print(c.fetchone())
	
		# print('Test4')
		
		# conn.commit()
		# conn.close() #closes connection to the config database
		
	# @tasks.loop(seconds=5.0)
	# async def updateDBLoop(): #main DB Update loop
		# print('Test')
		# if not Client.serverID==0:
			# print('Test2')
			
			# updateDB()
			
			# print('DB Updated for Server ID: '+str(Client.serverID)+'!')
		
	# updateDBLoop.start()