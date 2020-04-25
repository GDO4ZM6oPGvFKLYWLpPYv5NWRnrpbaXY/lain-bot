import discord
from discord.ext import commands

description = '''Test'''

class Client:

	bot = commands.Bot(command_prefix='k!', description=description)
	
	token = open("token.txt", "r")	