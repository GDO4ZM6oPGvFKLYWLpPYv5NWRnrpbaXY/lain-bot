import discord
from discord.ext import commands
import os
import json

description = '''Test'''

class Client:

	serverID = 0

	prefix = ">"
	bot = commands.Bot(command_prefix=prefix, description=description) #sets up the bot

	al_json = json.load(open(os.getcwd()+"/modules/anime/config/alID.json", 'r'))
	# @bot.check
	# async def check_serverID(ctx):
		# global serverID
		# Client.serverID = ctx.guild.id
		# print('Global check complete! Server ID: '+str(Client.serverID))
		# return Client.serverID
