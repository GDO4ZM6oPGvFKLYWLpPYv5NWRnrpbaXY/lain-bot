import discord

from .client import Client

bot = Client.bot

class Events:
	
	@bot.event
	async def on_ready():
		print('Kotori-san is ready to go!')