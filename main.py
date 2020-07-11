import os
from dotenv import load_dotenv
import logging

from modules.core.client import Client
from modules.core.events import Events
from modules.core.cogs import Cogs
#from modules.esportsclub import EsportsClub # for commands / features for UW-Madison Esports Club

bot = Client.bot

class Main:

	logging.basicConfig(filename='main.log', filemode='w', level=logging.DEBUG)

	esports = "FALSE"

	os.chdir(os.path.dirname(os.path.abspath(__file__))) #changes cwd to project root

	load_dotenv()
	TOKEN = os.getenv("BOT_TOKEN")

	bot.run(TOKEN) #runs the Discord bot using one of the above tokens
