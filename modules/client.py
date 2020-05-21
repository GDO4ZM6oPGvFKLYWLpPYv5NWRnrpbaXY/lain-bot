import discord
from discord.ext import commands

description = '''Test'''

class Client:

	serverID = 0

	bot = commands.Bot(command_prefix='k!', description=description) #sets up the bot

	@bot.check
	async def check_serverID(ctx):
		# global serverID
		Client.serverID = ctx.guild.id
		print('Global check complete! Server ID: '+str(Client.serverID))
		serverID = client.serverID
		return Client.serverID
