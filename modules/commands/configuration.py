import discord
from discord.ext import commands

from modules.core.client import Client
from modules.config.config import Config

bot = Client.bot

class Configuration(commands.Cog):

	@bot.group()
	async def config():
		if ctx.invoked_subcommand is None:
			await ctx.send('Invalid config command passed...')

	@config.command(pass_context=True)
	async def channel(ctx):
		serverID = str(ctx.guild.id)
		channelID = str(ctx.channel.id)
		Config.cfgUpdate(serverID, "Bot Channel", channelID)
		await ctx.send("Bot channel successfully updated to here!")

	@config.command(pass_context=True)
	async def where(ctx):
		serverID = str(ctx.guild.id)
		try:
			result = Config.cfgRead(serverID, "Bot Channel")
			await ctx.send(Config.cfgRead(serverID, "Bot Channel"))
		except:
			await ctx.send("Error!")
