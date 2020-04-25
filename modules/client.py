import discord
from discord.ext import commands

description = '''Test'''

game = discord.Game("with her phone") #sets the game the bot is currently playing

class Client:
	bot = commands.Bot(command_prefix='k!', description=description) #sets up the bot
	
	@bot.event
	async def on_ready():
		await bot.change_presence(status=discord.Status.online, activity=game)