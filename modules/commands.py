import youtube_dl
import ffmpeg

import discord
from discord.ext import commands

import random

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
		embed.set_author(name='音無小鳥', url='https://www.project-imas.com/wiki/Kotori_Otonashi', icon_url='https://raw.githubusercontent.com/SigSigSigurd/kotori-san-bot/master/search.png')
		embed.set_footer(text=safebooruTagsTogether)
		
		await channel.send(embed=embed)
	
	@bot.command(pass_context=True)
	async def serverID(ctx): #returns the serverID, mainly for debug purposes
		await ctx.send('Server ID: '+str(Client.serverID))