import discord, logging, re, json, time, asyncio, os, subprocess, math, copy
from discord.ext import commands
logger = logging.getLogger(__name__)

from modules.core.resources import Resources
from modules.anime.anilist2 import Anilist2
from modules.music.search import Themes

class Songs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def op_old(self, ctx, *args):
        try:
            await _search(self.bot, ctx, "OP", ' '.join(args))
        except:
            pass

    @commands.command()
    async def ed_old(self, ctx, *args):
        try:
            await  _search(self.bot, ctx, "ED", ' '.join(args))
        except:
            pass

    @commands.command()
    async def songs(self, ctx, *args):
        try:
            await _search_all(self.bot, ctx, ' '.join(args))
        except Exception as e:
            print(e)

    @commands.command()
    async def op(self, ctx, *args):
        try:
            await _search_specific(self.bot, ctx, "OP", ' '.join(args))
        except:
            pass

    @commands.command()
    async def ed(self, ctx, *args):
        try:
            await _search_specific(self.bot, ctx, "ED", ' '.join(args))
        except:
            pass

async def _search(bot, ctx, kind, search):
    if not search:
        return

    await ctx.trigger_typing()

    show = search
    num = ''
    ver = ''

    parts = search.split(' ')

    if len(parts) > 1:
        try: 
            tmp = int(parts[0])
            num = parts[0]
            show = ' '.join(parts[1:])
        except: 
            pass

        parts = show.split(' ')
        if len(parts) > 1 and (parts[0][0] == 'V' or parts[0][0] == 'v'):
            try:
                tmp = int(parts[0][1:])
                ver = parts[0].capitalize()
                show = ' '.join(parts[1:])
            except:
                pass

    print(f"Searching for show='{show}' kind='{kind}' num='{num}' ver='{ver}'")
    try:
        anime = await Anilist2.aniSearch(Resources.session, show, isAnime=True)
        title = str(anime['data']['anime']['title']['romaji'])
        showUrl = anime['data']['anime']['siteUrl']
        showPic = anime['data']['anime']['coverImage']['extraLarge']
        mal = str(anime['data']['anime']['idMal'])
    except:
        return await ctx.send("Show not found!")

    data = None
    async with Resources.session.get(f"https://themes.moe/api/themes/{mal}", raise_for_status=False) as resp:
        if not resp:
            return await ctx.send("Search resources offline right now. Try again later!")
        
        if resp.status != 200:
            return await ctx.send("Error getting data!")

        data = await resp.text()

    try:
        data = json.loads(data)
        data = data[0]['themes']
    except:
        return await ctx.send("Error getting data!")

    exact = None
    approx = None

    def __parse(e):
        r = re.search(f"(OP|ED)(\d*)( *)(V\d+|)", e['themeType'])
        if not r:
            return None
        return { "kind": r.group(1), "num": r.group(2), "ver": r.group(4), "name": e['themeName'], "link": e['mirror']['mirrorURL'], "notes": e['mirror']['notes'] }

    for e in data:
        e = __parse(e)
        if not e:
            continue

        if kind == e['kind'] and num == e['num'] and ver == e['ver']:
            exact = e
            break

        if not approx and kind == e['kind'] and num == e['num']:
            approx = e
            continue

        if not approx and kind in e['kind']:
            approx = e
            continue

    pick = exact
    if not pick:
        pick = approx

    if not pick:
        return await ctx.send("Not found")
            
    pickS = f"{pick['kind']}{pick['num']}"
    if pick['ver']:
        pickS += " " + pick['ver']
    if pick['notes']:
        pickS += " (" + pick['notes'] + ")"


    embed = discord.Embed(
        title=pick['name'],
        color=discord.Color.orange(),
        url=pick['link']
    )
    embed.set_author(name=title, url=showUrl, icon_url=showPic)
    embed.set_footer(
        text=pickS,
        icon_url='https://external-content.duckduckgo.com/ip3/themes.moe.ico'
    )

    info = []
    if 'Spoiler' in pick['notes']:
        info.append("video contains spoilers")
    if 'NSFW' in pick['notes']:
        info.append("video is NSFW")
    if info:
        embed.add_field(name='Info', value='\n'.join(info))

    msg = await ctx.send(embed=embed)

    def check(reaction, user):
        return user != msg.author and str(reaction.emoji) == '🔗'

    await msg.add_reaction('🔗')

    try:
        reaction, author = await bot.wait_for('reaction_add', timeout=10.0, check=check)
    except asyncio.TimeoutError:
        await msg.clear_reactions()
    else:
        await ctx.send(pick['link'])

async def _show_song(bot, ctx, data, song):
    embed = discord.Embed(
        title=song.title,
        color=discord.Color.orange(),
        url=song.url
    )
    embed.set_author(name=data.title, url=data.url, icon_url=data.cover)
    embed.set_footer(
        text=str(song.variant),
        icon_url='https://external-content.duckduckgo.com/ip3/themes.moe.ico'
    )

    info = []
    if 'Spoiler' in song.flags:
        info.append("video contains spoilers")
    if 'NSFW' in song.flags:
        info.append("video is NSFW")
    if info:
        embed.add_field(name='Info', value='\n'.join(info))

    if song.artists:
        embed.add_field(name="Artist(s)", value=song.artists_str())

    await ctx.send(embed=embed)

async def _prompt_selection(bot, ctx, msg, data):
    selectors = copy.deepcopy(Resources.selectors)
    msgs = []
    assoc = {}
    i = 0

    def p(s):
        if not selectors:
            return f"- {s}"
        return f"{selectors.pop(0)} {s}"

    await msg.delete()
    embed = discord.Embed(
        title=data.title,
        color=discord.Color.orange(),
        description="*None*" if not data.songs else '\n'.join(map(p, data.songs)),
        url=data.url
    )
    embed.set_thumbnail(url=data.cover)
    msgs.append(await ctx.send(embed=embed))
    selectors = copy.deepcopy(Resources.selectors)

    for option in data.songs:
        if not selectors:
            break
        selector = selectors.pop(0)
        if i == 20:
            i = 0
            msgs.append(await ctx.send("-"))
        assoc[selector] = option
        try:
            await msgs[-1].add_reaction(selector)
        except:
            break
        i += 1

    ignore = []
    def check(reaction, user):
        return reaction.message in msgs and user != msgs[-1].author and str(reaction.emoji) in assoc and str(reaction.emoji) not in ignore

    start = time.time()
    while time.time() - start < 30:
        timeout = 30 - (time.time() - start)
        try:
            reaction, author = await bot.wait_for('reaction_add', timeout=timeout, check=check)
        except asyncio.TimeoutError:
            for msg in msgs:
                await msg.clear_reactions()
            break
        else:
            selection = str(reaction.emoji)
            ignore.append(selection)
            for msg in msgs:
                await msg.clear_reaction(reaction)
            if selection not in assoc:
                for msg in msgs:
                    await msg.clear_reactions()
                return await ctx.send("lol no")
            await _show_song(bot, ctx, data, assoc[selection])
    for msg in msgs:
        await msg.clear_reactions()
    for msg in msgs[1:]:
        await msg.delete()


async def _search_specific(bot, ctx, kind, search):
    if not search:
        return

    await ctx.trigger_typing()

    show = search
    num = 1
    ver = 1

    parts = search.split(' ')

    if len(parts) > 1:
        try: 
            tmp = int(parts[0])
            num = tmp
            show = ' '.join(parts[1:])
        except: 
            pass

        parts = show.split(' ')
        if len(parts) > 1 and (parts[0][0] == 'V' or parts[0][0] == 'v'):
            try:
                tmp = int(parts[0][1:])
                ver = tmp
                show = ' '.join(parts[1:])
            except:
                pass

    print(f"Searching for show='{show}' kind='{kind}' num='{num}' ver='{ver}' from '{search}'")

    try:
        search = Themes.search_animethemesmoe(show)
    except Themes.NoResultsError as e:
        return await ctx.send(f"{e.message}")
    except Exception as e:
        return await ctx.send(f"Status: {e.status}\nMsg: {e.message}")

    songs = [s for s in search.songs if s.variant.kind == kind]

    if not songs:
        return await ctx.send("No results")

    exact = None
    approx = songs[0]
    for song in songs:
        print(f"{song} [{song.variant.sequence}, {song.variant.version}]")
        if song.variant.sequence == num:
            if song.variant.version == ver:
                exact = song
                break
            
            if song.variant.version < approx.variant.version:
                approx = song
                
    pick = exact
    if not pick:
        pick = approx

    await _show_song(bot, ctx, search, pick)


async def _search_all(bot, ctx, show):
    if not show:
        return

    await ctx.trigger_typing()

    try:
        search = Themes.search_animethemesmoe(show)
    except Themes.NoResultsError as e:
        return await ctx.send(f"{e.message}")
    except Exception as e:
        return await ctx.send(f"Status: {e.status}\nMsg: {e.message}")

    embed = discord.Embed(
        title=search.title,
        color=discord.Color.orange(),
        description="*None*" if not search.songs else '\n'.join(map(lambda s: str(s), search.songs)),
        url=search.url
    )
    embed.set_thumbnail(url=search.cover)

    msg = await ctx.send(embed=embed)

    # await msg.add_reaction('🎶')

    # def check(reaction, user):
    #     return user != msg.author and str(reaction.emoji) == '🎶'

    # try:
    #     reaction, author = await bot.wait_for('reaction_add', timeout=25.0, check=check)
    # except asyncio.TimeoutError:
    #     await msg.clear_reactions()
    # else:
    #     await msg.clear_reactions()
    #     await _prompt_selection(bot, ctx, msg, search)

