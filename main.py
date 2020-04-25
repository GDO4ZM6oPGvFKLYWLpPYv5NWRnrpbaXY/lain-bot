import discord
from discord.ext import commands

from modules.events import Events

description = '''Test'''

bot = commands.Bot(command_prefix='k!', description=description)

game = discord.Game("with her phone")

class Main:
		
	bot.run('NzAzMDYxNDg1NzgxMzg1MzU4.XqJJYw.df4dW8LQEKlS0D-wYrt0uSqFtrs') #runs the Discord bot