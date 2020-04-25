import youtube_dl
import ffmpeg

import discord
from discord.ext import commands

from .client import Client
from .config import Config
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
	async def safebooru(ctx, tags):
	
		channel = bot.get_channel(Config._botChannel)
		picture = Safebooru.booruSearch(tags)
		
		safebooruImageURL = Safebooru.booruSearch(tags)
		
		embed = discord.Embed(
			title = tags,
			color = discord.Color.green(),
			url = safebooruImageURL
		)
		
		embed.set_image(url=safebooruImageURL)
		embed.set_author(name='音無小鳥', url='https://www.project-imas.com/wiki/Kotori_Otonashi', icon_url='https://raw.githubusercontent.com/SigSigSigurd/kotori-san-bot/master/avatar.png')
		
		await channel.send(embed=embed)