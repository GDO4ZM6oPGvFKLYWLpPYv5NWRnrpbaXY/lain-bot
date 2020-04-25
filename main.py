import os
from os import path

import discord
from discord.ext import commands

from modules.client import Client
from modules.config import Config
from modules.commands import Commands
from modules.events import Events

bot = Client.bot
	
class Main:
	
	tokenTXT = "None"
	token = "None"
	tokenHeroku = "None"
	
	if path.exists("token.txt"): #retrives the token from the root directory (for testing)
		tokenTXT = open("token.txt", "r")
		token = str(tokenTXT.read())
	
	tokenHeroku = str(os.environ.get('BOT_TOKEN')) #retrives BOT_TOKEN from Heroku

	if not tokenHeroku == "None": 
		token = tokenHeroku
		
	bot.run(token) #runs the Discord bot using one of the above tokens