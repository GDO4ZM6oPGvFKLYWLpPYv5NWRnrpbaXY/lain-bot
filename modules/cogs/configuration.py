import logging
from discord.ext import commands
from discord.ext.commands import has_permissions
logger = logging.getLogger(__name__)

from modules.core.resources import Resources

class Configuration(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	@commands.group()
	async def config(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('Invalid config command passed...')

	@config.command()
	@has_permissions(administrator=True)
	async def channel(self, ctx):
		serverID = str(ctx.guild.id)
		channelID = str(ctx.channel.id)
		Resources.config.cfgUpdate(serverID, "Bot Channel", channelID)
		await ctx.send("Bot channel successfully updated to here!")

	@config.command()
	async def where(self, ctx):
		serverID = str(ctx.guild.id)
		try:
			result = Resources.config.cfgRead(serverID, "Bot Channel")
			await ctx.send(Resources.config.cfgRead(serverID, "Bot Channel"))
		except:
			await ctx.send("Error!")

	@config.command()
	@has_permissions(administrator=True)
	async def welcome(self, ctx):
		try:
			if Resources.config.cfgRead(str(ctx.guild.id), "welcomeChannel")==ctx.channel.id:
				Resources.config.cfgUpdate(str(ctx.guild.id), "welcomeChannel", 0)
				Resources.config.cfgUpdate(str(ctx.guild.id), "welcomeOn", False)
				await ctx.send("Disabled welcome messages in this channel!")
			elif Resources.config.cfgRead(str(ctx.guild.id), "welcomeChannel")!=0:
				Resources.config.cfgUpdate(str(ctx.guild.id), "welcomeChannel", ctx.channel.id)
				Resources.config.cfgUpdate(str(ctx.guild.id), "welcomeOn", True)
				await ctx.send("Moved and enabled welcome messages to this channel!")
			else: #this is seperate just in case, i forgot why while coding
				Resources.config.cfgUpdate(str(ctx.guild.id), "welcomeChannel", ctx.channel.id)
				Resources.config.cfgUpdate(str(ctx.guild.id), "welcomeOn", True)
				await ctx.send("Enabled welcome messages in this channel!")
		except:
			await ctx.send("error! LOL!")

	@config.command()
	@has_permissions(administrator=True)
	async def welcomemsg(self, ctx):
		msg = str(ctx.message.content)[(len(ctx.prefix) + len('config welcomemsg ')):]
		try:
			Resources.config.cfgUpdate(str(ctx.guild.id), "welcomeMsg", msg)
			await ctx.send("Updated welcome message!")
		except:
			logger.exception("Error sending error message.")
			await ctx.send("Error!")
