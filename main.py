import os, sys, logging, logging.handlers, atexit
from dotenv import load_dotenv
load_dotenv()

from modules.core.client import Client
from modules.core.events import Events
from modules.core.cogs import Cogs
#from modules.esportsclub import EsportsClub # for commands / features for UW-Madison Esports Club

file_handler = logging.handlers.RotatingFileHandler(
	'main.log', encoding='utf-8', maxBytes=2 * 1024**2, backupCount=5)
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.ERROR)
logging.basicConfig(level=logging.DEBUG, handlers=[
	stream_handler, file_handler])

# Log unhandled exceptions
def log_exception(exc_type, exc_value, tb):
	if issubclass(exc_type, KeyboardInterrupt):
		sys.__excepthook__(exc_type, exc_value, tb)
		return
	logging.critical(
		"Uncaught exception", exc_info=(exc_type, exc_value, tb))
sys.excepthook = log_exception

os.chdir(os.path.dirname(os.path.abspath(__file__))) #changes cwd to project root

TOKEN = os.getenv("BOT_TOKEN")

# Clean up on close
def exit_cleanup():
	Client.session.close_session() #close session after bot shuts down
	logging.info('Shut down.')

atexit.register(exit_cleanup)

if not TOKEN:
	logging.critical('No bot token provided.')
else:
	logging.info("Starting up...")
	Client.bot.run(TOKEN) #runs the Discord bot using one of the above tokens
