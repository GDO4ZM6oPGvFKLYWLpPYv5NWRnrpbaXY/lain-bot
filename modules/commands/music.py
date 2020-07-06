import discord
from discord.ext import commands
from discord.utils import get
import youtube_dl as ytdl
import ffmpeg
import random

from modules.core.client import Client
from modules.music.radio import Radio
from modules.music.themes import Themes
from modules.anime.anilist import Anilist

bot = Client.bot

class Music(commands.Cog):

    @bot.group()
    async def radio(ctx):
        if ctx.invoked_subcommand is None:
                await ctx.send('Invalid radio command passed...')

    @radio.command(pass_context=True)
    async def start(ctx):
        await ctx.send('Starting radio')
        # r/a/dio link
        url = 'https://stream.r-a-d.io/main.mp3'
        await join(ctx, url)

    @radio.command(pass_context=True)
    async def info(ctx):
        r = Radio.information()
        try:
            # variables
            main = r['main']
            song = main['np']
            q = main['queue']
            djname = main['dj']['djname']
            djimage = 'https://r-a-d.io/api/dj-image/' + str(main['dj']['djimage'])
            bitrate = str(main['bitrate'])
            listeners = str(main['listeners'])

            embed = discord.Embed(
                    title = 'R/a/dio Information',
                    color = discord.Color.red(),
                    url = 'https://r-a-d.io/'
                )

            embed.set_author(name=djname, url='https://r-a-d.io/staff', icon_url=djimage)

            # now playing
            embed.add_field(name='Now Playing', value=song, inline=False)

            # queued songs
            i = 1
            out = ''
            for s in q:
                out += str(i) + '. ' + s['meta'] + '\n'
                i += 1
            embed.add_field(name='Queue', value=out, inline=False)

            embed.set_footer(text='Listeners: {0}, Bitrate: {1}'.format(listeners, bitrate), icon_url='https://r-a-d.io/assets/logo_image_small.png')

            await ctx.send(embed=embed)
        except:
            await ctx.send('Error retrieving data')

    @bot.command(pass_context=True)
    async def yt(ctx, url):
        YTDL_OPTS = {
            "default_search": "ytsearch",
            "format": "bestaudio/best",
            "quiet": True,
            "extract_flat": "in_playlist"
        }
        try:
            with ytdl.YoutubeDL(YTDL_OPTS) as ydl:
                info = ydl.extract_info(url, download=False)

                if '_type' in info and info['_type'] == 'playlist':
                    await ctx.send('playlist not currently supported, playing first video...')
                    await join(ctx, info['entries'][0]['url'])
                else:
                    embed = discord.Embed(
                        title = info['title'],
                        color = discord.Color.red(),
                        url = info['webpage_url']
                    )

                    embed.set_author(name=info['uploader'], url=info['channel_url'])
                    embed.set_thumbnail(url=info['thumbnails'][0]['url'])
                    embed.set_footer(text='YouTube', icon_url='https://www.thermalwoodcanada.com/images/youtube-play-button-transparent-background-4.png')
                    await ctx.send(embed=embed)

                    await join(ctx, info['formats'][len(info['formats']) - 9]['url'])
        except Exception as e:
            await ctx.send(str(e))
    
    @bot.command(pass_context=True, aliases=['leave', 'radio stop', 'radio leave'])
    async def stop(ctx):
        try:
            channel = ctx.author.voice.channel
            voice = get(bot.voice_clients, guild=ctx.guild)

            if voice and voice.is_connected():
                await voice.disconnect()
                queues.clear()
            else:
                await ctx.send('Not connected to a voice channel')
        except AttributeError as a:
            print(a)
            await ctx.send('Not in a voice channel')
        except Exception as e:
            print(e)
            await ctx.send('Unexpected error')

    @bot.command(pass_context=True)
    async def pause(ctx):
        try:
            channel = ctx.author.voice.channel
            voice = get(bot.voice_clients, guild=ctx.guild)

            if voice and voice.is_connected() and voice.is_playing():
                voice.pause()
                await ctx.send('Paused')
        except AttributeError as a:
            print(a)
            await ctx.send('Not in a voice channel')
        except Exception as e:
            print(e)
            await ctx.send('Unexpected error')

    @bot.command(pass_context=True)
    async def resume(ctx):
        try:
            channel = ctx.author.voice.channel
            voice = get(bot.voice_clients, guild=ctx.guild)

            if voice and voice.is_connected() and voice.is_paused():
                voice.resume()
                await ctx.send('Resumed')
        except AttributeError as a:
            print(a)
            await ctx.send('Not in a voice channel')
        except Exception as e:
            print(e)
            await ctx.send('Unexpected error')

    @bot.command(pass_context=True, aliases=['next'])
    async def skip(ctx):
        try:
            channel = ctx.author.voice.channel
            voice = get(bot.voice_clients, guild=ctx.guild)

            if voice and voice.is_connected() and (voice.is_playing() or voice.is_paused):
                voice.stop()
                await ctx.send('Skipped')
        except AttributeError as a:
            print(a)
            await ctx.send('Not in a voice channel')
        except Exception as e:
            print(e)
            await ctx.send('Unexpected error')

    @bot.command(pass_context=True)
    async def clear(ctx):
        if len(queues) == 0:
            await ctx.send('Nothing in queue')
        else:
            queues.clear()
            await ctx.send('Queue cleared')

    @bot.command(pass_context=True)
    async def op(ctx, num):
        # 1 = opening
        t = 1
        build = parse(ctx, num)

        # show to search for
        show = build['show']
        # which opening to pick
        num = build['num']

        # first get list of openings from openings.moe
        songs = Themes.openingsMoe()

        if show == '':
            pick = random.choice(songs)
            show = pick['source']
            select = pick['title']
        else:
            select = 'Opening ' + num

        # anilist data
        anime = Anilist.aniSearch(show)

        # assign variables
        try:
            english = str(anime['data']['Media']['title']['english'])
            romaji = str(anime['data']['Media']['title']['romaji'])
            showUrl = anime['data']['Media']['siteUrl']
            showPic = anime['data']['Media']['coverImage']['extraLarge']
            year = anime['data']['Media']['startDate']['year']
            mal = str(anime['data']['Media']['idMal'])
            sId = anime['data']['Media']['id']
        except:
            await ctx.send('Invalid show')

        # get rid of null returns
        if english == 'None':
            english = romaji
        elif romaji == 'None':
            romaji == english

        parts = Themes.search(english.lower(), romaji.lower(), sId, show, select, songs)
        found = False
        try:
            embed = discord.Embed(
                    title = parts['big'],
                    color = discord.Color.orange(),
                    url = parts['video']
                )

            embed.set_author(name=parts['title'], url=showUrl, icon_url=showPic)
            embed.set_footer(text=parts['op/ed'], icon_url='https://openings.moe/assets/logo/512px.png')
            await ctx.send(embed=embed)

            await join(ctx, parts['video'])
        except Exception as e:
            print(e)
            found = True

        if found:
            try:
                parts = Themes.themesMoe(year, mal, t, num)
                big = num
                embed = discord.Embed(
                        title = parts['name'],
                        color = discord.Color.orange(),
                        url = parts['video']
                )
                embed.set_author(name=romaji, url=showUrl, icon_url=showPic)
                embed.set_footer(text=select, icon_url='https://external-content.duckduckgo.com/ip3/themes.moe.ico')
                await ctx.send(embed=embed)

                await join(ctx, parts['video'])
            except Exception as e:
                print(e)
                await ctx.send('*' + english + '*, ' + select + ' not found in database')

    @bot.command(pass_context=True)
    async def ed(ctx, num):
        # 2 = ending
        t = 2
        build = parse(ctx, num)

        # show to search for
        show = build['show']
        # which ending to pick
        num = build['num']

        # first get list of openings from openings.moe
        songs = Themes.openingsMoe()

        if show == '':
            pick = random.choice(songs)
            show = pick['source']
            select = pick['title']
        else:
            select = 'Ending ' + num

        # anilist data
        anime = Anilist.aniSearch(show)

        # search for ED
        try:
            english = str(anime['data']['Media']['title']['english'])
            romaji = str(anime['data']['Media']['title']['romaji'])
            showUrl = anime['data']['Media']['siteUrl']
            showPic = anime['data']['Media']['coverImage']['extraLarge']
            year = anime['data']['Media']['startDate']['year']
            mal = str(anime['data']['Media']['idMal'])
            sId = anime['data']['Media']['id']
        except:
            await ctx.send('Invalid show')

        # get rid of null returns
        if english == 'None':
            english = romaji
        elif romaji == 'None':
            romaji == english

        parts = Themes.search(english, romaji, sId, show, select, songs)
        found = False
        try:
            embed = discord.Embed(
                    title = parts['big'],
                    color = discord.Color.orange(),
                    url = parts['video']
                )

            embed.set_author(name=parts['title'], url=showUrl, icon_url=showPic)
            embed.set_footer(text=parts['op/ed'], icon_url='https://openings.moe/assets/logo/512px.png')
            await ctx.send(embed=embed)

            await join(ctx, parts['video'])
        except Exception as e:
            print(e)
            found = True

        if found:
            try:
                parts = Themes.themesMoe(year, mal, t, num)
                big = num
                embed = discord.Embed(
                        title = parts['name'],
                        color = discord.Color.orange(),
                        url = parts['video']
                )
                embed.set_author(name=romaji, url=showUrl, icon_url=showPic)
                embed.set_footer(text=select, icon_url='https://external-content.duckduckgo.com/ip3/themes.moe.ico')
                await ctx.send(embed=embed)

                await join(ctx, parts['video'])
            except Exception as e:
                print(e)
                await ctx.send('*' + english + '*, ' + select + ' not found in database')

# join a voice channel and play link
async def join(ctx, url):
	global voice
	try:
		# get voice channel
		channel = ctx.author.voice.channel
		if channel != None:
			# join channel
			voice = get(bot.voice_clients, guild=ctx.guild)

			if voice and voice.is_connected():
				# play music
				Radio.players[ctx.guild.id] = voice

			else:
				voice = await channel.connect()

			await play(ctx, voice, url)
	except AttributeError as a:
		print(a)
		await ctx.send('User is not in a channel.')
	except Exception as e:
		print(e)
		await ctx.send('Unexpected error')

async def play(ctx, voice, url):
	def check_queue():
		qnum = len(queues)
		if qnum != 0:
			next = queues.pop()
			voice.play(discord.FFmpegPCMAudio(next), after=lambda e: check_queue())
		else:
			queues.clear()

	if voice.is_playing():
		await add(ctx, url)
	else:
		voice.play(discord.FFmpegPCMAudio(url), after=lambda e: check_queue())

queues = []

async def add(ctx, url):
	queues.insert(0, url)

	await ctx.send('**{0}** in queue'.format(len(queues)))

# helper functions for vn and anilist search
def parse(ctx, num):
		# determine which op/ed should be played
		show = ''
		try:
			int(num[0])
			# get show name
			show = str(ctx.message.content)[(len(ctx.prefix) + len('op ' + str(num) + ' ')):]
		except ValueError as v:
			print(v)
			if len(num) >= 2:
				num = '1'
				show = str(ctx.message.content)[(len(ctx.prefix) + len('op ')):]
				#await ctx.send('Choose which OP you want to play first (1, 2, 3...)')
		except IndexError as f:
			print(f)

		return {'show' : show, 'num' : num}
