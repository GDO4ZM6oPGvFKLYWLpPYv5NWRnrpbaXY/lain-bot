import json
import requests
import praw
import random
import re

import os, logging
from dotenv import load_dotenv

from modules.anime.anilist import Anilist

load_dotenv()

themes_id = os.getenv("THEMES_ID")
themes_secret = os.getenv("THEMES_SECRET")
themes_agent = os.getenv("THEMES_AGENT")

class Themes():
    def openingsMoe():
        # get all openings & info
        songs = requests.get('https://openings.moe/api/list.php').json()
        return songs

    def search(english, romaji, sId, show, select, songs):
        found = True
        for i in range(2):
            for song in songs:
                title = song['source']
                ltitle = title.lower()
                opening = song['title']
                if (english in ltitle or romaji in ltitle) and select in opening:
                    if Anilist.aniSearch(title)['data']['Media']['id'] != sId:
                        continue
                    #print('\n' + english + '\n' + romaji + '\n' + ltitle + '\n' + str(english.lower() in ltitle or romaji.lower() in ltitle) + '\n\n')
                    video = 'https://openings.moe/video/' + song['file'] + '.mp4'
                    try:
                        big = song['song']['artist'] + ' - ' + song['song']['title']
                    except Exception as e:
                        logging.exception('Exception looking up theme.')
                        big = 'Video'
                        #await ctx.send('Playing **' + opening + '** of *' + title + '*')
                    return {'big' : big, 'video' : video, 'found' : True, 'title': title, 'op/ed': opening}
            english = show

        return {'found': False}

    def themesMoe(year, mal, which, num):
        reddit = praw.Reddit(client_id=themes_id, client_secret=themes_secret, user_agent=themes_agent)

        which = {
            1 : 'OP',
            2 : 'ED'
        }[which]

        if int(year) < 2000:
            year = str(year)
            year = year[2] + '0s'

        contains = ''
        for wikipage in reddit.subreddit('animethemes').wiki:
            if str(wikipage.name) == str(year):
                contains = wikipage
                break

        md = contains.content_md.split('\n')

        first = '/anime/' + mal + '/'
        second = str(which) + str(num)
        search = first
        info = ''
        for line in md:
            if search in line:
                if search == first:
                    search = second
                else:
                    info = line.split('|')
                    break

        if '\"' in info[0]:
            name = info[0].split('\"')[1]
        else:
            name = 'Video'

        video = re.search("(?P<url>https?://[^\s]+)", info[1]).group("url").replace(')', '')

        return {'video' : video, 'name' : name, 'info': info}
