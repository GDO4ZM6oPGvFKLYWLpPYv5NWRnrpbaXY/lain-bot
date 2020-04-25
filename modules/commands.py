import youtube_dl
import ffmpeg
import discord
from discord.ext import commands
import random
import sqlite3

from .client import Client
from .config import Config
from .events import Events
from .safebooru import Safebooru

bot = Client.bot

class Commands:

	players = {}
	
	@bot.command(pass_context=True)
	async def join(ctx):
		channel = ctx.message.author.voice.channel
		await bot.connect(channel)

	@bot.command(pass_context=True)
	async def leave(ctx):
		server = ctx.message.server
		voice_client = bot.voice_client_in(server)
		await voice_client.disconnect()

	@bot.command(pass_context=True)
	async def play(ctx, url):
		server = ctx.message.server
		voice_client = bot.voice_client_in(server)
		player = await voice_client.create_ytdl_player(url)
		players[server.id] = player
		player.start()
		
	@bot.command(pass_context=True)
	async def safebooru(ctx, tags): #looks up images on safebooru
	
		channel = ctx.message.channel
		
		safebooruSearch = Safebooru.booruSearch(tags)
		
		safebooruImageURL = safebooruSearch[0]
		safebooruPageURL = safebooruSearch[1]
		safebooruTagsTogether = safebooruSearch[2]
		
		embed = discord.Embed(
			title = tags,
			description = 'Is this what you were looking for, producer?',
			color = discord.Color.green(),
			url = safebooruPageURL
		)
		
		embed.set_image(url=safebooruImageURL)
		embed.set_author(name='音無小鳥', url='https://www.project-imas.com/wiki/Kotori_Otonashi', icon_url='https://raw.githubusercontent.com/SigSigSigurd/kotori-san-bot/master/assets/search.png')
		embed.set_footer(text=safebooruTagsTogether)
		
		await channel.send(embed=embed)
	
	@bot.command(pass_context=True)
	async def serverID(ctx): #returns the serverID, mainly for debug purposes
		await ctx.send('Server ID: '+str(Client.serverID))
		
	@bot.command(pass_context=True)
	async def checkConfig(ctx, id): #takes the server id number to check the config databases
	
		t = (id,)
		
		conn = sqlite3.connect('db/config.db') #connects to the config database
		c = conn.cursor()
		
		c.execute('Select * FROM servers WHERE serverID=?', t)
		await ctx.send(c.fetchone())
		
		conn.commit()
		conn.close() #closes connection to the config database
		
	# @bot.command(pass_context=True)
	# async def updateConfig(ctx, setting, value): #modifies the server information
		
		# s = (setting)
		# v = (value)
		# t = (Client.serverID,)
		# # guildName = get_guild(Client.serverID)
		# guildName = 'Test'
		# guildID = Client.serverID
		
		# conn = sqlite3.connect('db/config.db') #connects to the config database
		# c = conn.cursor()
		
		# c.execute('SELECT * FROM servers WHERE serverID=?', t)
		# if not c.fetchone():
			# c.execute('INSERT INTO servers VALUES (guildID, guildName, 0, 0, "Welcome!", 0, "Bye!")')
		
		# c.execute('UPDATE servers SET s = v WHERE serverID=?', t)
		
		# conn.commit()
		# conn.close() #closes connection to the config database