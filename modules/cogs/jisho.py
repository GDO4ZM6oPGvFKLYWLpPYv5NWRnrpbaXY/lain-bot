import logging, discord
logger = logging.getLogger(__name__)

from discord.ext import commands

from modules.core.client import Client

class Jisho(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx, err):
        logger.exception("Error during jisho command.")
        try:
            await ctx.send('error!', file=discord.File(os.getcwd() + '/assets/lain_err_sm.png'))
        except:
            pass

    @commands.command(aliases=['j'])
    async def jisho(self, ctx, *, search):
        await ctx.trigger_typing()

        if not search:
            return await ctx.send('I need something to search')

        async with Client.session.get('https://jisho.org/api/v1/search/words?keyword='+search) as resp:
            if resp.status != 200:
                return await ctx.send('I could not contact jisho.org')
            
            try:
                j = await resp.json()
            except:
                return await ctx.send('I could not read the jisho.org response')
            else:
                if 'data' not in j:
                    return await ctx.send('I could not read the jisho.org response')

            if not j['data']:
                return await ctx.send('No results')

            result = j['data'][0]

            tags = []
            readings = []
            definitions = []

            t = []
            t.extend(result['tags'])
            t.extend(result['jlpt'])
            if result['is_common']:
                t.append('common')

            for tag in t:
                tags.append(f"`{tag}`")            
            
            r = {}
            b = []
            for writing in result['japanese']:
                word = writing['word'] if 'word' in writing else None
                reading = writing['reading'] if 'reading' in writing else None

                if not word and not reading:
                    continue

                if word and reading:
                    if word in r:
                        r[word].append(reading)
                    else:
                        r[word] = [reading]
                elif not reading:
                    if word in r:
                        r[word].append(reading)
                    else:
                        r[word] = []
                elif not word:
                    b.append(reading)
            
            if b:
                readings.append(f"{', '.join(b)}")
            for reading in r:
                line = f"{reading} ({', '.join(r[reading])})"
                readings.append(line)

            for sense in result['senses']:
                piece = f"*{', '.join(sense['parts_of_speech'])}*\n"
                for i in range(0, len(sense['english_definitions'])):
                    piece += f"{i+1}. {sense['english_definitions'][i]}\n"
                definitions.append(piece)

            if not tags:
                tags = ['None']

            if not readings:
                readings = ['None']

            if not definitions:
                definitions = ['None']

            embed = discord.Embed(title="Result", description='', color=0x8abc83)
            embed.add_field(name="Readings", value='\n'.join(readings), inline=True)
            embed.add_field(name="Tags", value=' '.join(tags), inline=True)
            embed.add_field(name="Definitions", value='\n'.join(definitions), inline=False)
            embed.set_footer(text='info from jisho.org')

            await ctx.send(embed=embed)