import os
from os import path
import json
import discord
from discord.ext import commands

from modules.client import Client
from modules.config import Config
from modules.commands import Commands
from modules.events import Events
from modules.safebooru import Safebooru

bot = Client.bot

class Main:

	tokenTXT = "None"
	token = "None"
	tokenEnv = "None"

	if path.exists("config.json"): #retrives the token from the root directory (for testing)
		with open("config.json", 'r') as config_json:
			json_data = json.load(config_json)
			token = str(json_data["token"])

	#tokenEnv = str(os.environ.get('BOT_TOKEN')) #retrives BOT_TOKEN from Heroku/whatever

	#if not tokenEnv == "None":
	#	token = tokenEnv

	bot.run(token) #runs the Discord bot using one of the above tokens
