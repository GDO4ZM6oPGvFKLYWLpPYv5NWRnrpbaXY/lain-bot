from discord.ext import commands

class Client:

	prefix = ">"
	bot = commands.Bot(command_prefix=prefix) #sets up the bot
