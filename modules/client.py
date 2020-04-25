import discord
from discord.ext import commands
from boto.s3.connection import S3Connection

description = '''Test'''

class Client:
	bot = commands.Bot(command_prefix='k!', description=description) #sets up the bot