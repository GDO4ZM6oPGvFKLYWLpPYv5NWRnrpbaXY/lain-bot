from .profile import MALProfile
from .query import MyAnimeListQuery

class Description:
    label = 'myanimelist'
    lists = ['anime', 'manga']
    profile = MALProfile
    query = MyAnimeListQuery
    link_fn = lambda id: f"https://myanimelist.net/profile/{id}"
    time_between_queries = 15