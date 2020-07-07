import discord
from discord.ext import commands
import os

from modules.core.client import Client

bot = Client.bot

class Memes:

    # @bot.group()
    # async def memes(ctx):
        # if ctx.invoked_subcommand is None:
            # await ctx.send('Invalid xiii command passed...')

    @bot.command(pass_context=True)
    async def momoko(ctx):
        with open(os.getcwd()+"/assets/memes/momoko.jpg", 'rb') as fp:
            await ctx.send(file=discord.File(fp, 'momoko.jpg'))

    @bot.command(pass_context=True)
    async def simp(ctx):
        with open(os.getcwd()+"/assets/memes/simp.png", 'rb') as fp:
            await ctx.send(file=discord.File(fp, 'simp.png'))

    @bot.command(pass_context=True)
    async def kawamori(ctx):
        with open(os.getcwd()+"/assets/memes/kawamori.png", 'rb') as fp:
            await ctx.send(file=discord.File(fp, 'kawamori.png'))
