import os, logging
from dotenv import load_dotenv
load_dotenv()

from modules.core.client import Client
from modules.core.events import Events
from modules.core.cogs import Cogs
#from modules.esportsclub import EsportsClub # for commands / features for UW-Madison Esports Club


logging.basicConfig(filename='main.log', filemode='w', level=logging.DEBUG)

os.chdir(os.path.dirname(os.path.abspath(__file__))) #changes cwd to project root

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
	print('Not bot token provided')
else:
	try:
		Client.bot.run(TOKEN) #runs the Discord bot using one of the above tokens
		Client.session.close_session() #close session after bot shuts down
	except:
		pass
