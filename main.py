import discord
from discord.ext import commands

#from modules.events import Events
from modules.client import Client

description = '''Test'''

bot = Client.bot

game = discord.Game("with her phone")
token = Client.token

class Main:
	
	bot.run(token.read())