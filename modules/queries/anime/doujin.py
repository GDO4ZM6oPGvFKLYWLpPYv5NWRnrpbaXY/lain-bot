import requests
import json
from bs4 import BeautifulSoup as Soup

class Doujin():
    def metaSearch(id, token):
        url = 'https://api.e-hentai.org/api.php'
        e = {
            "method": "gdata",
            "gidlist": [
                [int(id),str(token)]
            ],
            "namespace": 1
        }

        response = requests.post(url, json=e)
        return response.json()['gmetadata'][0]
    
    def tagSearch(tags):
        g = requests.get('https://e-hentai.org/?f_search=' + tags.strip().replace(' ', '+'))
        if g.status_code == 200:
            html = Soup(g.content, 'html.parser')
            r = []
            link = 'https://e-hentai.org/'
            for a in html.find_all('a', href=True):
                if link + 'g/' in a['href'] or link + 's/' in a['href']:
                    r.append(a['href'])
        else:
            r = None
        # list of links to doujins
        return r