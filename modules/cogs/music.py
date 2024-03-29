import discord, youtube_dl as ytdl, random, logging
from discord.ext import commands
from discord.utils import get
logger = logging.getLogger(__name__)

from modules.queries.music.radio import Radio
from modules.queries.music.themes import Themes
from modules.queries.anime.anilist import Anilist

class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def radio(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid radio command passed...')

    @radio.command()
    async def start(self, ctx):
        await ctx.send('Starting radio')
        # r/a/dio link
        url = 'https://stream.r-a-d.io/main.mp3'
        await join(self.bot, ctx, url)

    @radio.command()
    async def info(self, ctx):
        r = Radio.information()
        try:
            # variables
            main = r['main']
            song = main['np']
            q = main['queue']
            djname = main['dj']['djname']
            djimage = 'https://r-a-d.io/api/dj-image/' + \
                str(main['dj']['djimage'])
            bitrate = str(main['bitrate'])
            listeners = str(main['listeners'])

            embed = discord.Embed(
                title='R/a/dio Information',
                color=discord.Color.red(),
                url='https://r-a-d.io/'
            )

            embed.set_author(
                name=djname, url='https://r-a-d.io/staff', icon_url=djimage)

            # now playing
            embed.add_field(name='Now Playing', value=song, inline=False)

            # queued songs
            i = 1
            out = ''
            for s in q:
                out += str(i) + '. ' + s['meta'] + '\n'
                i += 1
            embed.add_field(name='Queue', value=out, inline=False)

            embed.set_footer(text='Listeners: {0}, Bitrate: {1}'.format(
                listeners, bitrate), icon_url='https://r-a-d.io/assets/logo_image_small.png')

            await ctx.send(embed=embed)
        except:
            logger.exception("Error during radio command.")
            await ctx.send('Error retrieving data')

    @commands.command()
    async def yt(self, ctx, url):
        if 'youtube.com/' not in url:
            url = str(ctx.message.content)[(len(ctx.prefix) + len('yt ')):]

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
                    # await ctx.send('playlist not currently supported, playing first video...')
                    info = ydl.extract_info(
                        info['entries'][0]['url'], download=False)

                embed = discord.Embed(
                    title=info['title'],
                    color=discord.Color.red(),
                    url=info['webpage_url']
                )

                embed.set_author(
                    name=info['uploader'], url=info['channel_url'])
                embed.set_thumbnail(url=info['thumbnails'][0]['url'])
                embed.set_footer(
                    text='YouTube', icon_url='https://www.thermalwoodcanada.com/images/youtube-play-button-transparent-background-4.png')
                await ctx.send(embed=embed)

                await join(self.bot, ctx, info['formats'][3]['url'])
        except Exception as e:
            logger.exception('Error during youtube command')
            await ctx.send(str(e))

    @commands.command(aliases=['leave', 'radio stop', 'radio leave'])
    async def stop(self, ctx):
        try:
            channel = ctx.author.voice.channel
            voice = get(self.bot.voice_clients, guild=ctx.guild)

            if voice and voice.is_connected():
                await voice.disconnect()
                queues.clear()
            else:
                await ctx.send('Not connected to a voice channel')
        except AttributeError as a:
            await ctx.send('Not in a voice channel')
        except Exception as e:
            logger.exception('Error in music stop command.')
            await ctx.send('Unexpected error')

    @commands.command()
    async def pause(self, ctx):
        try:
            channel = ctx.author.voice.channel
            voice = get(self.bot.voice_clients, guild=ctx.guild)

            if voice and voice.is_connected() and voice.is_playing():
                voice.pause()
                await ctx.send('Paused')
        except AttributeError as a:
            logger.exception('Not in a voice channel')
            await ctx.send('Not in a voice channel')
        except Exception as e:
            logger.exception('Error pausing music.')
            await ctx.send('Unexpected error')

    @commands.command()
    async def resume(self, ctx):
        try:
            channel = ctx.author.voice.channel
            voice = get(self.bot.voice_clients, guild=ctx.guild)

            if voice and voice.is_connected() and voice.is_paused():
                voice.resume()
                await ctx.send('Resumed')
        except AttributeError as a:
            logger.exception('Not in a voice channel')
            await ctx.send('Not in a voice channel')
        except Exception as e:
            logger.exception('Error resuming music.')
            await ctx.send('Unexpected error')

    @commands.command(aliases=['next'])
    async def skip(self, ctx):
        try:
            channel = ctx.author.voice.channel
            voice = get(self.bot.voice_clients, guild=ctx.guild)

            if voice and voice.is_connected() and (voice.is_playing() or voice.is_paused):
                voice.stop()
                await ctx.send('Skipped')
            else:
                await ctx.send('Nothing to skip')
        except AttributeError as a:
            logger.exception('Not in a voice channel')
            await ctx.send('Not in a voice channel')
        except Exception as e:
            logger.exception('Error skipping music.')
            await ctx.send('Unexpected error')

    @commands.command()
    async def clear(self, ctx):
        if len(queues) == 0:
            await ctx.send('Nothing in queue')
        else:
            queues.clear()
            await ctx.send('Queue cleared')

# join a voice channel and play link
async def join(bot, ctx, url):
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
        logger.exception('User is not in a voice channel')
        if 'animethemes.moe' not in url:
            await ctx.send('User is not in a channel.')
    except Exception as e:
        logger.exception('Error joining voice channel.')
        await ctx.send('Unexpected error')

async def play(ctx, voice, url):
    def check_queue():
        qnum = len(queues)
        if qnum != 0:
            next = queues.pop()
            voice.play(discord.FFmpegPCMAudio(
                next, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options='-vn'), after=lambda e: check_queue())
        else:
            queues.clear()

    if voice.is_playing():
        await add(ctx, url)
    else:
        try:
            voice.play(discord.FFmpegPCMAudio(
                url, before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', options='-vn'), after=lambda e: check_queue())
        except Exception as e:
            await ctx.send(e)

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
        show = str(ctx.message.content)[
            (len(ctx.prefix) + len('op ' + str(num) + ' ')):]
    except ValueError as v:
        logger.exception('Error during music parsing')
        if len(num) >= 2:
            num = '1'
            show = str(ctx.message.content)[(len(ctx.prefix) + len('op ')):]
            # await ctx.send('Choose which OP you want to play first (1, 2, 3...)')
    except IndexError as f:
        logger.exception('Error during music parsing')

    return {'show': show, 'num': num}
