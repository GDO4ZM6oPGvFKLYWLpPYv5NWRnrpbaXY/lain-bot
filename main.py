import os
from os import path

import discord
from discord.ext import commands

from modules.client import Client
from modules.events import Events

bot = Client.bot
	
class Main:
	
	tokenTXT = "None"
	token = "None"
	tokenHeroku = "None"
	
	if path.exists("token.txt"):
		tokenTXT = open("token.txt", "r")
		token = str(tokenTXT.read())
	
	tokenHeroku = str(os.environ.get('BOT_TOKEN'))

	if not tokenHeroku == "None": #retrives BOT_TOKEN from Heroku
		token = tokenHeroku
		
	bot.run(token) #runs the Discord bot