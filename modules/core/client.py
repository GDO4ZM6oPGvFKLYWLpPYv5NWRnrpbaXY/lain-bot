from discord.ext import commands
from modules.core.session import Session

class Client:
	
	session = Session(raise_for_status=True)
	
	prefix = ">"
	bot = commands.Bot(command_prefix=prefix) #sets up the bot
