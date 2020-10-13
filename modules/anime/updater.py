import discord, os, sys, json, time, datetime, pytz, traceback
from discord.ext import tasks, commands

from modules.core.database import Database
from modules.anime.anilist2 import Anilist2
from modules.core.img_gen import ImageGenerator
from modules.core.client import Client

animeModFields = ['status', 'score', 'progress']
animeBase = {
    'status': 'empty',
    'score': 0,
    'progress': 0
}
mangaModFields = ['status', 'score', 'progress', 'progressVolumes']
mangaBase = {
    'status': 'empty',
    'score': 0,
    'progress': 0,
    'progressVolumes': 0
}

class Updater(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.cursor = Database.userCollection().find()
        self.al_update.start()
        self.cleanup_img_gen.start()

    def cog_unload(self):
        self.al_update.cancel()
        self.cleanup_img_gen.cancel()


    def fieldsModified(self, e1, e2, fieldsToCheck):
        return [field for field in fieldsToCheck if e1[field] != e2[field]]

    def animeModified(self, e1, e2):
        return self.fieldsModified(e1, e2, animeModFields)

    def mangaModified(self, e1, e2):
        return self.fieldsModified(e1, e2, mangaModFields)


    def syncAnimeList(self, old_list, fetched_list, scoreFormat):
        changes = { 'msgs': [], 'imgUrls': [] }
        new_list = {}

        for lst in fetched_list['lists']:
            for fetched_entry in lst['entries']:
                # set up data differences
                old_entry = old_list.get(str(fetched_entry['mediaId']))
                if not old_entry:
                    old_entry = animeBase

                modified = self.animeModified(old_entry, fetched_entry)

                title = fetched_entry['media']['title']['romaji']
                if not title:
                    title = fetched_entry['media']['title']['english']
                if not title:
                    title = fetched_entry['media']['title']['native']
                if not title:
                    title = ':COULD NOT GET VALID TITLE:'

                banner = fetched_entry['media']['bannerImage']
                cover = fetched_entry['media']['coverImage']['large']

                prog = fetched_entry['progress']
                prog_str = str(prog)
                prog_old = old_entry['progress']
                prog_old_inc_str = str(prog_old+1)
                prog_delta = prog - prog_old

                score = fetched_entry['score']
                score_str = str(score)
                score_old = old_entry['score']
                score_old_str = str(score_old)

                status = fetched_entry['status']
                status_old = old_entry['status']

                msg = ''
                if scoreFormat != 'CHNG' and 'score' in modified and not ('status' in modified and status == 'COMPLETED'):
                # handle if score changed except if entry changed to completed since 
                # changing to complete will show score if it's there
                    msg = 'score of ' + title + ' changed: '
                    msg += Database.scoreFormated(score_old, scoreFormat) + ' ➔ ' + Database.scoreFormated(score, scoreFormat)
                    
                    changes['msgs'].append(msg)
                    changes['imgUrls'].append({ 'banner': banner, 'cover': cover})

                if 'status' in modified:
                # handle changes of adding to lists where score/progress doesn't matter
                    if status == 'PLANNING' or (prog == 0 and status in ['CURRENT', 'REPEATING']):
                        msg = title + ' added to ' + status.lower() + ' list'
                    elif status in ['DROPPED', 'PAUSED']:
                        msg = status.lower() + ' ' + title
                        if prog > 0:
                            msg += ' on episode ' + prog_str
                    elif status == 'COMPLETED':
                        msg = status.lower() + ' ' + title
                        if score > 0:
                            msg += ' with a score of ' + Database.scoreFormated(score, scoreFormat)
                    else:
                        msg = ''

                    if msg:
                        changes['msgs'].append(msg)
                        changes['imgUrls'].append({ 'banner': banner, 'cover': cover})
                        new_list[str(fetched_entry['mediaId'])] = Database.formListEntryFromAnilistEntry(fetched_entry, anime=True)
                        continue

                if prog_delta == 1:
                # handle when progress is incremented by 1 i.e. watched 1 episode
                    msg = ''
                    if status == 'REPEATING':
                        msg += 're'
                    msg += 'watched episode ' + prog_str + ' of ' + title

                    changes['msgs'].append(msg)
                    changes['imgUrls'].append({ 'banner': banner, 'cover': cover})
                elif prog_delta > 1:
                # i'm not gonna handle if progress is reduced
                    msg = ''
                    if status == 'REPEATING':
                        msg += 're'
                    msg += 'watched episodes ' + prog_old_inc_str + '-' + prog_str + ' of ' + title

                    changes['msgs'].append(msg)
                    changes['imgUrls'].append({ 'banner': banner, 'cover': cover})
                else:
                    pass

                new_list[str(fetched_entry['mediaId'])] = Database.formListEntryFromAnilistEntry(fetched_entry, anime=True)

        return { 'changes': changes, 'new_list': new_list }


    def syncMangaList(self, old_list, fetched_list, scoreFormat):
        changes = { 'msgs': [], 'imgUrls': [] }
        new_list = {}

        for lst in fetched_list['lists']:
            for fetched_entry in lst['entries']:
                # set up data differences
                old_entry = old_list.get(str(fetched_entry['mediaId']))
                if not old_entry:
                    old_entry = mangaBase

                modified = self.mangaModified(old_entry, fetched_entry)

                title = fetched_entry['media']['title']['romaji']
                if not title:
                    title = fetched_entry['media']['title']['english']
                if not title:
                    title = fetched_entry['media']['title']['native']
                if not title:
                    title = ':COULD NOT GET VALID TITLE:'

                banner = fetched_entry['media']['bannerImage']
                cover = fetched_entry['media']['coverImage']['large']

                prog = fetched_entry['progress']
                prog_str = str(prog)
                prog_old = old_entry['progress']
                prog_old_inc_str = str(prog_old+1)
                prog_delta = prog - prog_old

                progVol = fetched_entry['progressVolumes']
                progVol_str = str(progVol)
                progVol_old = old_entry['progressVolumes']
                progVol_old_inc_str = str(progVol_old+1)
                progVol_delta = progVol - progVol_old

                score = fetched_entry['score']
                score_str = str(score)
                score_old = old_entry['score']
                score_old_str = str(score_old)

                status = fetched_entry['status']
                status_old = old_entry['status']

                msg = ''
                if scoreFormat != 'CHNG' and 'score' in modified and not ('status' in modified and status == 'COMPLETED'):
                # handle if score changed except if entry changed to completed since 
                # changing to complete will show score if it's there
                    msg = 'score of ' + title + ' changed: '
                    msg += Database.scoreFormated(score_old, scoreFormat) + ' ➔ ' + Database.scoreFormated(score, scoreFormat)
                    
                    changes['msgs'].append(msg)
                    changes['imgUrls'].append({ 'banner': banner, 'cover': cover})

                if 'status' in modified:
                # handle changes of adding to lists where score/progress doesn't matter
                    if status == 'PLANNING' or (prog == 0 and progVol == 0 and status in ['CURRENT', 'REPEATING']):
                        msg = title + ' added to ' + status.lower() + ' list'
                    elif status in ['DROPPED', 'PAUSED']:
                        msg = status.lower() + ' ' + title
                        if prog > 0:
                            msg += ' on episode ' + prog_str
                    elif status == 'COMPLETED':
                        msg = status.lower() + ' ' + title
                        if score > 0:
                            msg += ' with a score of ' + Database.scoreFormated(score, scoreFormat)
                    else:
                        msg = ''

                    if msg:
                        changes['msgs'].append(msg)
                        changes['imgUrls'].append({ 'banner': banner, 'cover': cover})
                        new_list[str(fetched_entry['mediaId'])] = Database.formListEntryFromAnilistEntry(fetched_entry, anime=False)
                        continue

                if prog_delta == 1:
                # handle when progress is incremented by 1 i.e. read 1 chapter
                    msg = ''
                    if status == 'REPEATING':
                        msg += 're'
                    msg += 'read chapter ' + prog_str + ' of ' + title

                    changes['msgs'].append(msg)
                    changes['imgUrls'].append({ 'banner': banner, 'cover': cover})
                elif prog_delta > 1:
                # i'm not gonna handle if progress is reduced
                    msg = ''
                    if status == 'REPEATING':
                        msg += 're'
                    msg += 'read chapters ' + prog_old_inc_str + '-' + prog_str + ' of ' + title

                    changes['msgs'].append(msg)
                    changes['imgUrls'].append({ 'banner': banner, 'cover': cover})
                else:
                    pass

                if progVol_delta == 1:
                # handle when progress is incremented by 1 i.e. read 1 volume
                    msg = ''
                    if status == 'REPEATING':
                        msg += 're'
                    msg += 'read volume ' + progVol_str + ' of ' + title

                    changes['msgs'].append(msg)
                    changes['imgUrls'].append({ 'banner': banner, 'cover': cover})
                elif progVol_delta > 1:
                # i'm not gonna handle if progress is reduced
                    msg = ''
                    if status == 'REPEATING':
                        msg += 're'
                    msg += 'read volumes ' + progVol_old_inc_str + '-' + progVol_str + ' of ' + title

                    changes['msgs'].append(msg)
                    changes['imgUrls'].append({ 'banner': banner, 'cover': cover})
                else:
                    pass

                new_list[str(fetched_entry['mediaId'])] = Database.formListEntryFromAnilistEntry(fetched_entry, anime=False)

        return { 'changes': changes, 'new_list': new_list }


    def limitChanges(self, changes, limit, imgLimit=8):
        aChMln = len(changes['animeChanges']['msgs'])
        mChMln = len(changes['mangaChanges']['msgs'])

        # get rid of entries with neither banner nor cover and use one in place of the other if just one missing
        for i in reversed(range(len(changes['animeChanges']['imgUrls']))):
            imgUrl = changes['animeChanges']['imgUrls'][i]
            if imgUrl['banner'] is None and imgUrl['cover'] is None:
                del changes['animeChanges']['imgUrls'][i]
            elif imgUrl['banner'] is None:
                imgUrl['banner'] = imgUrl['cover']
            elif imgUrl['cover'] is None:
                imgUrl['cover'] = imgUrl['banner']
            else:
                pass

        for i in reversed(range(len(changes['mangaChanges']['imgUrls']))):
            imgUrl = changes['mangaChanges']['imgUrls'][i]
            if imgUrl['banner'] is None and imgUrl['cover'] is None:
                del changes['mangaChanges']['imgUrls'][i]
            elif imgUrl['banner'] is None:
                imgUrl['banner'] = imgUrl['cover']
            elif imgUrl['cover'] is None:
                imgUrl['cover'] = imgUrl['banner']
            else:
                pass

        # remove duplicate imgUrls
        seen = set()
        new_lst = []
        for u in changes['animeChanges']['imgUrls']:
            if u['banner'] + u['cover'] not in seen:
                new_lst.append(u)
                seen.add(u['banner'] + u['cover'])
        changes['animeChanges']['imgUrls'] = new_lst

        seen = set()
        new_lst = []
        for u in changes['mangaChanges']['imgUrls']:
            if u['banner'] + u['cover'] not in seen:
                new_lst.append(u)
                seen.add(u['banner'] + u['cover'])
        changes['mangaChanges']['imgUrls'] = new_lst

        changes['animeChanges']['imgUrls'] = changes['animeChanges']['imgUrls'][:imgLimit]
        changes['mangaChanges']['imgUrls'] = changes['mangaChanges']['imgUrls'][:imgLimit]        
        
        # don't let msgs be longer than limit and add new msg if it is
        if changes['animeChanges']['msgs'] and  aChMln > limit:
            changes['animeChanges']['msgs'] = changes['animeChanges']['msgs'][:limit]
            changes['animeChanges']['msgs'].append('and ' + str(aChMln-limit) + ' other changes!')

        if changes['mangaChanges']['msgs'] and  mChMln > limit:
            changes['mangaChanges']['msgs'] = changes['mangaChanges']['msgs'][:limit]
            changes['mangaChanges']['msgs'].append('and ' + str(mChMln-limit) + ' other changes!')

        return changes


    # send user updates to servers
    async def sendChanges(self, user, changes):
        # check if there were any changes
        if not (changes['animeChanges']['msgs'] or changes['mangaChanges']['msgs']):
            return

        changes = self.limitChanges(changes, 6)

        # get all the guilds this user is apart of
        guildIdsWithUser = []
        for guild in self.bot.guilds:
            for member in guild.members:
                if str(member.id) == user['discordId']:
                    guildIdsWithUser.append(str(guild.id))

        mangaOnlyChannels = []
        animeOnlyChannels = []

        async for guild in Database.guild_find({'id': {'$in': guildIdsWithUser}}):
            for channel in guild['mangaMessageChannels']:
                c = self.bot.get_channel(int(channel))
                if c:
                    mangaOnlyChannels.append(c)
            for channel in guild['animeMessageChannels']:
                c = self.bot.get_channel(int(channel))
                if c:
                    animeOnlyChannels.append(c)

        # get_channel() returns None on failure so get rid of any of those
        mangaOnlyChannels = [x for x in mangaOnlyChannels if x is not None]
        animeOnlyChannels = [x for x in animeOnlyChannels if x is not None]

        # remove common elements and place into their own list
        # comboChannels = [self.bot.get_channel(int("756626065652449300"))]
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
            embeds[embed].set_footer(text='This message was posted ' + datetime.datetime.now(pytz.timezone('America/Chicago')).strftime('%b %d, %Y at %I:%M %p (CT)'))

        if user['profile']['avatar']['large']:
            for embed in embeds:
                embeds[embed].set_thumbnail(url=user['profile']['avatar']['large'])

        if changes['animeChanges']['msgs']:
            embeds['anime'].add_field(name="Updated their anime list: ", value='\n'.join(map(lambda x: '\• ' + x, changes['animeChanges']['msgs'])), inline=False)
            embeds['combo'].add_field(name="Updated their anime list: ", value='\n'.join(map(lambda x: '\• ' + x, changes['animeChanges']['msgs'])), inline=False)

        if changes['mangaChanges']['msgs']:
            embeds['manga'].add_field(name="Updated their manga list: ", value='\n'.join(map(lambda x: '\• ' + x, changes['mangaChanges']['msgs'])), inline=False)
            embeds['combo'].add_field(name="Updated their manga list: ", value='\n'.join(map(lambda x: '\• ' + x, changes['mangaChanges']['msgs'])), inline=False)

        # get time to use for any image generation
        uf = str(int(round(time.time()*1000)))

        animeImgLen = len(changes['animeChanges']['imgUrls'])
        mangaImgLen = len(changes['mangaChanges']['imgUrls'])

        if changes['mangaChanges']['msgs']:
            if mangaImgLen < 2:
                if mangaImgLen == 1:
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
            if animeImgLen < 2:
                if animeImgLen == 1:
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
            if animeImgLen + mangaImgLen < 2:
                if changes['animeChanges']['imgUrls']: 
                    embeds['combo'].set_image(url=changes['animeChanges']['imgUrls'][0]['banner'])
                elif changes['mangaChanges']['imgUrls']:
                    embeds['combo'].set_image(url=changes['mangaChanges']['imgUrls'][0]['banner'])
                else:
                    pass
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
    @tasks.loop(seconds=float(os.getenv('UPDATE_INTERVAL', 10)))
    async def al_update(self):
        # wait until bot is ready
        if not self.bot.is_ready():
            print('--warming up')
            return

        # next user in database iteration
        try:
            nextUser = await self.cursor.to_list(length=1)
        except Exception as e:
            print('--'+__file__+' :: unable to get next user in db')
            print(e)
            return

        if nextUser:
            # get local data
            user = nextUser[0]
            old_managaList = user['mangaList']
            old_animeList = user['animeList']

            # get anilist data
            try:
                fetched_user = await Anilist2.getUserData(Client.session, user['anilistId'])
            except Exception as e:
                print('--'+__file__+' :: unable to fetch user data from anilist')
                print(e)
                return
            else:
                # check for errors in query
                if not fetched_user or 'errors' in fetched_user:
                    print('update fail - either no user data or errors in query result: ')
                    print(fetched_user)
                    print('...continuing to next user')
                    return

            fetched_animeList = fetched_user['data']['animeList']
            fetched_mangaList = fetched_user['data']['mangaList']

            # find differences
            animeSync = self.syncAnimeList(old_animeList, fetched_animeList, Database.userScoreFormat(user, fetched_user))
            mangaSync = self.syncMangaList(old_managaList, fetched_mangaList, Database.userScoreFormat(user, fetched_user))

            # only send messages for set users
            if user['status']:
                try:
                    await self.sendChanges(user, {'animeChanges': animeSync['changes'], 'mangaChanges': mangaSync['changes']})
                except Exception as e:
                    print('could not send changes')
                    print(e)
                    print(traceback.format_exc())

            # update local user to match anilist
            await Database.user_update_one(
                {'_id': user['_id']}, 
                {'$set': {
                    'animeList': animeSync['new_list'], 
                    'mangaList': mangaSync['new_list'], 
                    'profile': fetched_user['data']['User'], 
                    'anilistName': fetched_user['data']['User']['name']
                    }
                }
            )

        else:
            # iterated all users in database. repeat
            await self.cursor.close()
            self.cursor = Database.userCollection().find()

    # delete any images created by the gerator
    @tasks.loop(minutes=4)
    async def cleanup_img_gen(self):
        try:
            files = [f for f in os.listdir(os.getcwd() + '/assets/img_gen/') if os.path.isfile(os.getcwd() + '/assets/img_gen/' + f)]
            for f in files:
                t = f.partition('_')[0]
                fmt = f[-3:]
                # remove jpgs older than a minute
                if fmt == 'jpg' and int(round(time.time()*1000)) - int(t) > 60000:
                    os.remove(os.getcwd() + '/assets/img_gen/' + f)
        except Exception as e:
            print('--'+__file__+' :: unable to delete images')
            print(e)