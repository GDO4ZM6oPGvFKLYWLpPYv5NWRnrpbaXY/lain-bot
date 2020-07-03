import discord
from discord.ext import commands
from discord.utils import get
import random
import sqlite3
import os
import json

from modules.core.client import Client
from modules.config.config import Config

from modules.commands.anime import Anime
from modules.commands.music import Music
from modules.commands.fighting import Fighting
from modules.commands.configuration import Configuration

bot = Client.bot

class Command:

	@bot.command(pass_context=True)
	async def serverID(ctx): #returns the serverID, mainly for debug purposes
		await ctx.send('Server ID: '+str(Client.serverID))
