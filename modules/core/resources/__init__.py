import pytz, os, aiohttp

from .database import Database
from .img_gen import ImageGenerator as img_gen
from .al2mal2al import Al2mal2al

db_url = 'mongodb://'+os.getenv('DBUSER')+':'+os.getenv('DBKEY')+'@' + os.getenv('DBPATH')
if not bool(os.getenv('NON_SRV_DB', default=False)):
    db_url = 'mongodb+srv://'+os.getenv('DBUSER')+':'+os.getenv('DBKEY')+'@' + os.getenv('DBPATH')

class Resources:
    session = None
    syncer_session = None
    user_col = Database(db_url, 'v2', 'users')
    guild_col = Database(db_url, 'v2', 'guilds')
    storage_col = Database(db_url, 'lain-bot', 'storage')
    timezone_str = 'US/Central'
    timezone = pytz.timezone(timezone_str)
    img_gen = img_gen
    removal_buffers = {}
    status_buffers = {}
    al2mal2al = Al2mal2al()

    selectors =  ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿', '🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '🟤', '🔺', '🔻', '🔸', '🔹', '🔶', '🔷', '🔳', '🔲', '▫️', '◼️', '◻️', '🟥', '🟧', '🟨', '🟩', '🟦', '🟪', '🟫', '♈', '♉', '♊', '♍', '♌', '♋', '♎', '♏', '♐', '♓', '♒', '♑', '⛎']

    @staticmethod
    async def init():
        Resources.session = aiohttp.ClientSession(raise_for_status=True)
        Resources.syncer_session = aiohttp.ClientSession()