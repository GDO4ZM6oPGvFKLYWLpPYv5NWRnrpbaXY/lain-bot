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
    user_col = Database(db_url, 'v2', 'users')
    guild_col = Database(db_url, 'v2', 'guilds')
    storage_col = Database(db_url, 'lain-bot', 'storage')
    timezone = pytz.timezone('US/Central')
    img_gen = img_gen

    selectors =  ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '🇰', '🇱', '🇲', '🇳', '🇴', '🇵', '🇶', '🇷', '🇸', '🇹', '🇺', '🇻', '🇼', '🇽', '🇾', '🇿', '🔴', '🟠', '🟡', '🟢', '🔵', '🟣', '🟤', '🔺', '🔻', '🔸', '🔹', '🔶', '🔷', '🔳', '🔲', '▫️', '◼️', '◻️', '🟥', '🟧', '🟨', '🟩', '🟦', '🟪', '🟫', '♈', '♉', '♊', '♍', '♌', '♋', '♎', '♏', '♐', '♓', '♒', '♑', '⛎']