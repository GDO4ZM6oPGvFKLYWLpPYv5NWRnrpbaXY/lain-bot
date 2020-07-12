import discord
from discord.ext import commands
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
