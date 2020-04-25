import discord
from discord.ext import commands

from modules.client import Client
from modules.events import Events


bot = Client.bot
token = open("token.txt", "r")

class Main:
		
	bot.run(token.read()) #runs the Discord bot