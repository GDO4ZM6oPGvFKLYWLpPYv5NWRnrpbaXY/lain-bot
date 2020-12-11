import pytz, os

from .session import Session
from .database import Database
from .img_gen import ImageGenerator as img_gen

db_url = 'mongodb://'+os.getenv('DBUSER')+':'+os.getenv('DBKEY')+'@' + os.getenv('DBPATH')
if not bool(os.getenv('NON_SRV_DB', default=False)):
    db_url = 'mongodb+srv://'+os.getenv('DBUSER')+':'+os.getenv('DBKEY')+'@' + os.getenv('DBPATH')

class Resources:
    session = Session(raise_for_status=True)
    syncer_session = Session()
    user2_col = Database(db_url, 'v2', 'users')
    guild2_col = Database(db_url, 'v2', 'guilds')
    storage_col = Database(db_url, 'lain-bot', 'storage')
    users_col = Database(db_url, 'lain-bot', 'users')
    guilds_col = Database(db_url, 'lain-bot', 'guilds')
    timezone = pytz.timezone('America/Chicago')
    img_gen = img_gen