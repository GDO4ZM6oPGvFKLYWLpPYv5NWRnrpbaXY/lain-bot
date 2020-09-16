import discord, os, sys, json, time
from discord.ext import tasks, commands

from modules.core.database import Database
from modules.anime.anilist2 import Anilist2
from modules.core.img_gen import ImageGenerator

class Updator(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cursor = Database.userCollection().find()
        self.al_update.start()
        self.cleanup_img_gen.start()

    def cog_unload(self):
        self.al_update.cancel()
        self.cleanup_img_gen.cancel()


    # helper function for getting the denominator for different scoring formats
    def scoreFormat(self, user):
        fmt = user['profile']['mediaListOptions']['scoreFormat']
        if fmt == 'POINT_100':
            return '100'
        elif fmt == 'POINT_10_DECIMAL' or fmt == 'POINT_10':
            return '10'
        elif fmt == 'POINT_5':
            return '5'
        else:
            return '3'


    def animeModified(self, old, new):
        test = True
        test = test and old['status'] == new['status']
        test = test and old['score'] == new['score']
        test = test and old['progress'] == new['progress']
        return not test


    def mangaModified(self, old, new):
        test = True
        test = test and old['status'] == new['status']
        test = test and old['score'] == new['score']
        test = test and old['progress'] == new['progress']
        test = test and old['progressVolumes'] == new['progressVolumes']
        return not test


    def syncAnimeList(self, old_list, fetched_list, scoreFormat):
        changes = { 'msgs': [], 'imgUrls': [] }
        new_list = {}

        for lst in fetched_list['lists']:
            for fetched_entry in lst['entries']:
                old_entry = old_list.get(str(fetched_entry['mediaId']))
                if old_entry:
                    if self.animeModified(old_entry, fetched_entry):
                        changes['imgUrls'].append({ 'banner': fetched_entry['media']['bannerImage'], 'cover': fetched_entry['media']['coverImage']['large']})
                        if old_entry['status'] != fetched_entry['status']:
                            if fetched_entry['status'] == 'COMPLETED':
                                msg = 'completed ' + old_entry['title']
                                if fetched_entry['score'] > 0:
                                    msg += ' with a score of ' + str(fetched_entry['score']) + '/' + scoreFormat
                                changes['msgs'].append(msg)
                            else:
                                msg = 'added ' + old_entry['title'] + ' to ' + fetched_entry['status'].lower() + ' list'
                                changes['msgs'].append(msg)
                        else:
                            if old_entry['score'] != fetched_entry['score']:
                                msg = 'score of ' + old_entry['title'] + ' changed: ' + str(old_entry['score']) + '/' + scoreFormat + ' -> ' + str(fetched_entry['score']) + '/' + scoreFormat
                                changes['msgs'].append(msg)
                            # does not handle if progress was reduced
                            if old_entry['progress'] < fetched_entry['progress']:
                                msg = 'watched '
                                if fetched_entry['status'] == 'REPEATING':
                                    msg = 'rewatched '
                                if fetched_entry['progress'] - old_entry['progress'] == 1:
                                    msg += 'episode ' + str(fetched_entry['progress']) + ' of ' + old_entry['title']
                                else:
                                    msg += 'episodes ' + str(old_entry['progress']+1) + '-' + str(fetched_entry['progress']) + ' of ' + old_entry['title']
                                changes['msgs'].append(msg)
                else:
                    # new entry from anilist
                    changes['imgUrls'].append({ 'banner': fetched_entry['media']['bannerImage'], 'cover': fetched_entry['media']['coverImage']['large']})
                    if fetched_entry['status'] == 'CURRENT':
                        msg = 'added ' + fetched_entry['media']['title']['romaji'] + ' to currently watching list'
                    else:
                        msg = 'added ' + fetched_entry['media']['title']['romaji'] + ' to ' + fetched_entry['status'].lower() + ' list'
                    changes['msgs'].append(msg)

                new_entry = {
                    'status': fetched_entry['status'],
                    'score': fetched_entry['score'],
                    'progress': fetched_entry['progress'],
                    'episodes': fetched_entry['media']['episodes'],
                    'title': fetched_entry['media']['title']['romaji']
                }
                new_list[str(fetched_entry['mediaId'])] = new_entry

        return { 'changes': changes, 'new_list': new_list }


    def syncMangaList(self, old_list, fetched_list, scoreFormat):
        changes = { 'msgs': [], 'imgUrls': [] }
        new_list = {}

        for lst in fetched_list['lists']:
            for fetched_entry in lst['entries']:
                old_entry = old_list.get(str(fetched_entry['mediaId']))
                if old_entry:
                    if self.mangaModified(old_entry, fetched_entry):
                        changes['imgUrls'].append({ 'banner': fetched_entry['media']['bannerImage'], 'cover': fetched_entry['media']['coverImage']['large']})
                        if old_entry['status'] != fetched_entry['status']:
                            if fetched_entry['status'] == 'COMPLETED':
                                msg = 'completed ' + old_entry['title']
                                if fetched_entry['score'] > 0:
                                    msg += ' with a score of ' + str(fetched_entry['score']) + '/' + scoreFormat
                                changes['msgs'].append(msg)
                            else:
                                msg = 'added ' + old_entry['title'] + ' to ' + fetched_entry['status'].lower() + ' list'
                                changes['msgs'].append(msg)
                        else:
                            if old_entry['score'] != fetched_entry['score']:
                                msg = 'score of ' + old_entry['title'] + ' changed: ' + str(old_entry['score']) + '/' + scoreFormat + ' -> ' + str(fetched_entry['score']) + '/' + scoreFormat
                                changes['msgs'].append(msg)
                            # does not handle if progress was reduced
                            if old_entry['progress'] < fetched_entry['progress']:
                                msg = 'read '
                                if fetched_entry['status'] == 'REPEATING':
                                    msg = 'reread '
                                if fetched_entry['progress'] - old_entry['progress'] == 1:
                                    msg += 'chapter ' + str(fetched_entry['progress']) + ' of ' + old_entry['title']
                                else:
                                    msg += 'chapters ' + str(old_entry['progress']+1) + '-' + str(fetched_entry['progress']) + ' of ' + old_entry['title']
                                changes['msgs'].append(msg)
                            if old_entry['progressVolumes'] < fetched_entry['progressVolumes']:
                                msg = 'read '
                                if fetched_entry['status'] == 'REPEATING':
                                    msg = 'reread '
                                if fetched_entry['progressVolumes'] - old_entry['progressVolumes'] == 1:
                                    msg += 'volume ' + str(fetched_entry['progressVolumes']) + ' of ' + old_entry['title']
                                else:
                                    msg += 'volumes ' + str(old_entry['progressVolumes']+1) + '-' + str(fetched_entry['progressVolumes']) + ' of ' + old_entry['title']
                                changes['msgs'].append(msg)
                else:
                    # new entry from anilist
                    changes['imgUrls'].append({ 'banner': fetched_entry['media']['bannerImage'], 'cover': fetched_entry['media']['coverImage']['large']})
                    if fetched_entry['status'] == 'CURRENT':
                        msg = 'added ' + fetched_entry['media']['title']['romaji'] + ' to currently reading list'
                    else:
                        msg = 'added ' + fetched_entry['media']['title']['romaji'] + ' to ' + fetched_entry['status'].lower() + ' list'
                    changes['msgs'].append(msg)

                new_entry = {
                    'status': fetched_entry['status'],
                    'score': fetched_entry['score'],
                    'progress': fetched_entry['progress'],
                    'progressVolumes': fetched_entry['progressVolumes'],
                    'chapters': fetched_entry['media']['chapters'],
                    'volumes': fetched_entry['media']['volumes'],
                    'title': fetched_entry['media']['title']['romaji']
                }
                new_list[str(fetched_entry['mediaId'])] = new_entry
                
        return { 'changes': changes, 'new_list': new_list }

    def limitChanges(self, changes, limit):
        aChMln = len(changes['animeChanges']['msgs'])
        mChMln = len(changes['mangaChanges']['msgs'])

        if changes['animeChanges']['msgs'] and  aChMln > limit:
            changes['animeChanges']['imgUrls'] = changes['animeChanges']['imgUrls'][:limit]
            changes['animeChanges']['msgs'] = changes['animeChanges']['msgs'][:limit]
            changes['animeChanges']['msgs'].append('and ' + str(aChMln-limit) + ' other changes!')

        if changes['mangaChanges']['msgs'] and  mChMln > limit:
            changes['mangaChanges']['imgUrls'] = changes['mangaChanges']['imgUrls'][:limit]
            changes['mangaChanges']['msgs'] = changes['mangaChanges']['msgs'][:limit]
            changes['mangaChanges']['msgs'].append('and ' + str(aChMln-limit) + ' other changes!')

        return changes

    # send user updates to servers
    async def sendChanges(self, user, changes):
        changes = self.limitChanges(changes, 8)

        botGuildIds = [guild.id for guild in self.bot.guilds]
        userEnableMangaGuildIds = user['mangaMessageGuilds']
        userEnableAnimeGuildIds = user['animeMessageGuilds']

        # get guild where user has activated messaging and are active in the bot
        mangaMessageGuilds = list(set(botGuildIds).intersection(userEnableMangaGuildIds))
        animeMessageGuilds = list(set(botGuildIds).intersection(userEnableAnimeGuildIds))

        mangaOnlyChannels = []
        animeOnlyChannels = []

        async for guild in Database.guildCollection().find({'id': {'$in': mangaMessageGuilds}}):
            for channel in guild['mangaMessageChannels']:
                mangaOnlyChannels.append(self.bot.get_guild(guild['id']).get_channel(channel))

        async for guild in Database.guildCollection().find({'id': {'$in': animeMessageGuilds}}):
            for channel in guild['animeMessageChannels']:
                animeOnlyChannels.append(self.bot.get_guild(guild['id']).get_channel(channel))

        comboChannels = []
        for i in reversed(range(len(mangaOnlyChannels))):
            mChn = mangaOnlyChannels[i]
            for aChn in animeOnlyChannels:
                if aChn.id == mChn.id:
                    comboChannels.append(mChn)
                    del mangaOnlyChannels[i]
                    animeOnlyChannels.remove(aChn)
                    break

        embeds = {
            'anime': discord.Embed(
                title = user['anilistName'],
                url = 'https://anilist.co/user/'+str(user['anilistId'])
            ),      
            'manga': discord.Embed(
                title = user['anilistName'],
                url = 'https://anilist.co/user/'+str(user['anilistId'])
            ),     
            'combo': discord.Embed(
                title = user['anilistName'],
                url = 'https://anilist.co/user/'+str(user['anilistId'])
            )
        }

        for embed in embeds:
            embeds[embed].set_thumbnail(url=user['profile']['avatar']['large'])

        if changes['animeChanges']['msgs']:
            embeds['anime'].add_field(name="Updated their anime list: ", value='\n'.join(map(lambda x: '\> ' + str(x),changes['animeChanges']['msgs'])), inline=False)
            embeds['combo'].add_field(name="Updated their anime list: ", value='\n'.join(map(lambda x: '\> ' + str(x),changes['animeChanges']['msgs'])), inline=False)

        if changes['mangaChanges']['msgs']:
            embeds['manga'].add_field(name="Updated their manga list: ", value='\n'.join(map(lambda x: '\> ' + str(x),changes['mangaChanges']['msgs'])), inline=False)
            embeds['combo'].add_field(name="Updated their manga list: ", value='\n'.join(map(lambda x: '\> ' + str(x),changes['mangaChanges']['msgs'])), inline=False)

        uf = str(int(round(time.time()*1000)))

        if changes['mangaChanges']['msgs']:
            if len(changes['mangaChanges']['imgUrls']) < 2:
                embeds['manga'].set_image(url=changes['mangaChanges']['imgUrls'][0]['banner'])
                for channel in mangaOnlyChannels:
                    await channel.send(embed=embeds['manga'])
            else:
                ImageGenerator.combineUrl(uf+'_manga.jpg', *[urls['cover'] for urls in changes['mangaChanges']['imgUrls']])
                embeds['manga'].set_image(url='attachment://'+uf+'_manga.jpg')
                for channel in mangaOnlyChannels:
                    f = discord.File(os.getcwd()+'/assets/img_gen/'+uf+'_manga.jpg', filename=uf+'_manga.jpg')
                    await channel.send(file=f, embed=embeds['manga'])

        if changes['animeChanges']['msgs']:
            if len(changes['animeChanges']['imgUrls']) < 2:
                embeds['anime'].set_image(url=changes['animeChanges']['imgUrls'][0]['banner'])
                for channel in animeOnlyChannels:
                    await channel.send(embed=embeds['anime'])
            else:
                ImageGenerator.combineUrl(uf+'_anime.jpg', *[urls['cover'] for urls in changes['animeChanges']['imgUrls']])
                embeds['anime'].set_image(url='attachment://'+uf+'_anime.jpg')
                for channel in animeOnlyChannels:
                    f = discord.File(os.getcwd()+'/assets/img_gen/'+uf+'_anime.jpg', filename=uf+'_anime.jpg')
                    await channel.send(file=f, embed=embeds['anime'])

        # channels that support manga and anime updates
        if changes['animeChanges']['msgs'] or changes['mangaChanges']['msgs']:
            if len(changes['animeChanges']['imgUrls']) + len(changes['mangaChanges']['imgUrls']) < 2:
                if changes['animeChanges']['imgUrls']: 
                    embeds['combo'].set_image(url=changes['animeChanges']['imgUrls'][0]['banner'])
                else:
                    embeds['combo'].set_image(url=changes['mangaChanges']['imgUrls'][0]['banner'])
                for channel in comboChannels:
                    await channel.send(embed=embeds['combo'])
            else:     
                urls = [urls['cover'] for urls in changes['animeChanges']['imgUrls']] + [urls['cover'] for urls in changes['mangaChanges']['imgUrls']]
                ImageGenerator.combineUrl(uf+'_combo.jpg', *urls)
                embeds['combo'].set_image(url='attachment://'+uf+'_combo.jpg')
                for channel in comboChannels:
                    f = discord.File(os.getcwd()+'/assets/img_gen/'+uf+'_combo.jpg', filename=uf+'_combo.jpg')
                    await channel.send(file=f, embed=embeds['combo'])


    # interate through each user in database keeping up to date with anilist
    @tasks.loop(seconds=4)
    async def al_update(self):
        # wait until bot is ready
        if not self.bot.is_ready():
            print('--warming up')
            return

        # next user in database iteration
        nextUser = await self.cursor.to_list(length=1)

        if nextUser:
            # get local data
            user = nextUser[0]
            old_managaList = user['mangaList']
            old_animeList = user['animeList']

            # get anilist data
            fetched_user = await Anilist2.getUserData(self.bot.get_cog('Session').session, user['anilistId'])
            fetched_animeList = fetched_user['data']['animeList']
            fetched_mangaList = fetched_user['data']['mangaList']

            # find differences
            animeSync = self.syncAnimeList(old_animeList, fetched_animeList, self.scoreFormat(user))
            mangaSync = self.syncMangaList(old_managaList, fetched_mangaList, self.scoreFormat(user))

            # do stuff if there were any changes detected
            try:
                await self.sendChanges(user, {'animeChanges': animeSync['changes'], 'mangaChanges': mangaSync['changes']})
            except:
                print('bots don\'t quit. ignore the discord.py errors.')

            # update local user to match anilist
            await Database.userCollection().update_one({'_id': user['_id']}, {'$set': {'animeList': animeSync['new_list'], 'mangaList': mangaSync['new_list'], 'profile': fetched_user['data']['User']}})

        else:
            # iterated all users in database. repeat
            await self.cursor.close()
            self.cursor = Database.userCollection().find()

    # delete any images created by the gerator
    @tasks.loop(minutes=30)
    async def cleanup_img_gen(self):
        files = [f for f in os.listdir(os.getcwd() + '/assets/img_gen/') if os.path.isfile(os.getcwd() + '/assets/img_gen/' + f)]
        for f in files:
            t = f.partition('_')[0]
            fmt = f[-3:]
            # remove jpgs and ones older than a minute
            if fmt == 'jpg' and int(round(time.time()*1000)) - int(t) > 60000:
                os.remove(os.getcwd() + '/assets/img_gen/' + f)