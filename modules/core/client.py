import discord
from discord.ext import commands
from modules.core.session import Session

class Client:
	intents = discord.Intents.default()
	intents.members = True 
	
	session = Session(raise_for_status=True)
	
	prefix = ">"
	bot = commands.Bot(command_prefix=prefix, intents=intents) #sets up the bot
