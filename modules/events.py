import discord

from .client import Client

bot = Client.bot

class Events:
	
	@bot.event
	async def on_ready():
		await bot.change_presence(status=discord.Status.online, activity=game)
		print('Kotori-san is ready to go!')