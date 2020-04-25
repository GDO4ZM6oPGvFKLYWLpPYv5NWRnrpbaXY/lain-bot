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
	
	if path.exists("token.txt"):
		tokenTXT = open("token.txt", "r")
		token = tokenTXT.read()
	
	tokenHeroku = os.environ.get('TOKEN')

	if tokenHeroku: #retrives TOKEN from Heroku
		token = tokenHeroku
		
	bot.run(token) #runs the Discord bot