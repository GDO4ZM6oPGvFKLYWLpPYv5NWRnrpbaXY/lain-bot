from .anilist import Description as anilist
from .myanimelist import Description as myanimelist

from enum import Enum

class Meta(str):
    __slots__ = ['Profile', 'list_names', 'Query', 'link', 'time_between_queries']

    def profile(self, profile=None):
        return self.Profile(**profile) if profile else self.Profile()

    def lists(self, lists=None):
        if lists:
            return lists
        else:
            d = {}
            for lst in self.list_names:
                d[lst] = {}
            return d

def _meta_gen(desc) -> Meta:
    var = Meta(desc.label)
    var.Profile = desc.profile
    var.list_names = desc.lists
    var.Query = desc.query
    var.link = desc.link_fn
    var.time_between_queries = desc.time_between_queries

    return var

class Services(Enum):
    anilist = anilist.label
    myanimelist = myanimelist.label

class Service:
    ANILIST = _meta_gen(anilist)
    MYANIMELIST = _meta_gen(myanimelist)

    def __new__(cls, service: str):
        if service == Service.ANILIST:
            return Service.ANILIST
        elif service == Service.MYANIMELIST:
            return Service.MYANIMELIST
        else:
            raise AttributeError(f"No service with name {service}")

    @staticmethod
    def all():
        return [Service.ANILIST, Service.MYANIMELIST]

    @staticmethod
    def active():
        return [Service.ANILIST, Service.MYANIMELIST]

    @staticmethod
    async def register(bot):
        from .syncer import Syncer
        from .commands import ServiceCommands
        from modules.core.resources import Resources

        await bot.add_cog(ServiceCommands(bot))
        
        for service in Service.active():
            Resources.removal_buffers[service] = set()
            Resources.status_buffers[service] = {}
            syncer = Syncer(bot, service, service.Query(), service.time_between_queries)
            bot.loop.create_task(syncer.loop())
