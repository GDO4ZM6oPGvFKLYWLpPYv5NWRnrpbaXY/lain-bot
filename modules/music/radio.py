import requests

class Radio():
    # radios on servers
    players = {}

    def information():
        r = requests.get('https://r-a-d.io/api')
        if r.status_code == 200:
            m = r.json()
        elif r.status_code == 400:
            m = 'Connection error'
        else:
            m = 'Unknown error'
        return m