from modules.core.loop import Loop
from modules.core.client import Client

from modules.cogs.anime import Anime
from modules.cogs.music import Music
from modules.cogs.fighting import Fighting
from modules.cogs.configuration import Configuration
from modules.cogs.memes import Memes
from modules.cogs.testing import Testing

from modules.esports.esportsclub import EsportsClub

class Cogs:
    Client.bot.add_cog(Memes(Client.bot))
    Client.bot.add_cog(Fighting(Client.bot))
    Client.bot.add_cog(Anime(Client.bot))
    Client.bot.add_cog(Configuration(Client.bot))
    Client.bot.add_cog(Music(Client.bot))
    Client.bot.add_cog(Testing(Client.bot))

    #temporary?
    Client.bot.add_cog(EsportsClub(Client.bot))

    Client.bot.add_cog(Loop(Client.bot, Anime.al_json))
