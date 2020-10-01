import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import os

from modules.core.client import Client

class Memes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # @commands.group()
    # async def memes(ctx):
        # if ctx.invoked_subcommand is None:
            # await ctx.send('Invalid xiii command passed...')

    @commands.command(pass_context=True)
    async def momoko(self, ctx):
        with open(os.getcwd()+"/assets/memes/momoko.jpg", 'rb') as fp:
            await ctx.send(file=discord.File(fp, 'momoko.jpg'))

    @commands.command(pass_context=True)
    async def simp(self, ctx):
        with open(os.getcwd()+"/assets/memes/simp.png", 'rb') as fp:
            await ctx.send(file=discord.File(fp, 'simp.png'))

    @commands.command(pass_context=True)
    async def kawamori(self, ctx):
        with open(os.getcwd()+"/assets/memes/kawamori.png", 'rb') as fp:
            await ctx.send(file=discord.File(fp, 'kawamori.png'))

    @commands.command(pass_context=True)
    async def tomino(self, ctx):
        with open(os.getcwd()+"/assets/memes/tomino.png", 'rb') as fp:
            await ctx.send(file=discord.File(fp, 'tomino.png'))

    @commands.command(pass_context=True)
    async def nagai(self, ctx):
        with open(os.getcwd()+"/assets/memes/nagai.png", 'rb') as fp:
            await ctx.send(file=discord.File(fp, 'nagai.png'))

    @commands.command(pass_context=True)
    async def anno(self, ctx):
        with open(os.getcwd()+"/assets/memes/anno.jpg", 'rb') as fp:
            await ctx.send(file=discord.File(fp, 'anno.jpg'))

    @commands.command(pass_context=True)
    async def gtab(self, ctx):
        with open(os.getcwd()+"/assets/memes/gtab.mp4", 'rb') as fp:
            await ctx.send(file=discord.File(fp, 'gtab.mp4'))

    @commands.command(pass_context=True)
    async def milky(self, ctx):
        await ctx.send("Milky Holmes represents the pandora'x box of the current century. Upon opening this metaphysical masterpiece you are greeted with a look directly into the inner depth of the human psyche. Every neuron fires at once, every muscle contracts at once, your retinas are bombarded with images and sound and smell and emotion and the wind swirls around you like a tornado as you begin to glow as if you were self immolating. Milky and Holmes are two things that should never logically go together and yet here we are. Now you may have guessed, \"Holmes\" refers to Holmes as in Sherlock Holmes, the master detective and famous crack addict; Milky Holmes decided to focus more on the crack addict part than any interpretation before. The pacing, the music, the art direction, it all elicits a feeling that I can only compare to what I imagine being hopped on those white rocks is like while the lights strobe and the music blares, what a life we live on this planet. Kiss your wife goodbye, tell your kids you love them, bone your dog goodbye, and get ready to walk the yellow brick plank, we're headed to a quadrochomatic party that never leaves your head.")
        await ctx.send("Allow me to set the stage. It's 3:00 AM, you're lying awake at night waiting for your brain to collapse in on itself so that you can finally escape this post modernist world for 3 or 4 hours. Suddenly, during your 4th prayer of the night a hole opens up in your vision from which a welcoming hand is extended. It hands you a letter with a beautiful hand pressed wax stamp, you open this letter and written by the great lord himself reads \"shove your fingers up your ass.\" This is what watching milky holmes is like. The devout understand, the sinners understand, but only true artists can appreciate the lengths that Milk and her homies will go for a laugh. When Ghandi said that the secret to true peace lies within ones soul, he meant this show's soul. Not you, not him, this is the one show who's soul can grant you inner peace in these trying times. After completing this 13 episode transcendental journey I was awarded with a PHD in modern philosophy and I was never bothered by the entropy of the universe again. In essence I became the closest being to god that exists, as I am now above that which I do not understand nor have a need to understand.")
 
    @commands.command(pass_context=True)
    async def good(self, ctx, *args):
        if len(args) and args[0] in ['bot', 'bot!']:
            await ctx.send('https://files.catbox.moe/jkhrji.png')

    @commands.command(pass_context=True)
    async def bad(self, ctx, *args):
        if len(args) and args[0] in ['bot', 'bot!']:
            await ctx.send('https://files.catbox.moe/bde830.gif')
