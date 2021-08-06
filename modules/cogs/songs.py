import discord, logging, re, json, time, asyncio, requests
from discord.ext import commands
logger = logging.getLogger(__name__)

from modules.core.resources import Resources
from modules.anime.anilist2 import Anilist2

class Songs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def op(self, ctx, *args):
        try:
            await _search(self.bot, ctx, "OP", ' '.join(args))
        except:
            pass

    @commands.command()
    async def ed(self, ctx, *args):
    #try:
        await  _search(self.bot, ctx, "ED", ' '.join(args))
    #except:
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
        year = anime['data']['anime']['startDate']['year']
        mal = str(anime['data']['anime']['idMal'])
        sId = anime['data']['anime']['id']
    except:
        return await ctx.send("Show not found!")

    data = None
    async with Resources.session2.get(f"https://themes.moe/api/themes/{mal}", raise_for_status=False) as resp:
        if not resp:
            return await ctx.send("Search resources offline right now. Try again later!")
        
        if resp.status != 200:
            return await ctx.send("Error getting data!")

        print("themes.moe responded")
        data = await resp.text()
        print("themes.moe data grabbed")

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


        
