from .profile import WeebProfile
from .query import AnilistQuery

class Description:
    label = 'anilist'
    lists = ['anime', 'manga']
    profile = WeebProfile
    query = AnilistQuery
    link_fn = lambda id: f"https://anilist.co/user/{id}"
    time_between_queries = 5