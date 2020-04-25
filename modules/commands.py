import youtube_dl
import ffmpeg

import discord
from discord.ext import commands

from .client import Client

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