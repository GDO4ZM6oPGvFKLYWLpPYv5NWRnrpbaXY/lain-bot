import discord

from .client import Client

bot = Client.bot
game = discord.Game("with her phone") #sets the game the bot is currently playing

class Events:
	
	@bot.event
	async def on_ready():
		print('Kotori-san is ready to go!')
		await bot.change_presence(status=discord.Status.online, activity=game)