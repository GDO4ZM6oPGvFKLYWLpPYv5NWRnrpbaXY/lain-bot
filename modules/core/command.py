import discord
from discord.ext import commands
from discord.utils import get
import random
import sqlite3

from modules.core.client import Client
from modules.config.config import Config

bot = Client.bot

class Command:

	@bot.command(pass_context=True)
	async def serverID(ctx): #returns the serverID, mainly for debug purposes
		await ctx.send('Server ID: '+str(Client.serverID))
