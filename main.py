import discord
from discord.ext import commands

from modules.client import Client
from modules.events import Events


bot = Client.bot
tokenTXT = open("token.txt", "r")
token = none

if os.environ.get('TOKEN') != 'None': #retrives TOKEN from Heroku
	token = os.environ.get('TOKEN')
else:
	token = tokenTXT.read()

class Main:
		
	#bot.run(token.read()) #runs the Discord bot
	