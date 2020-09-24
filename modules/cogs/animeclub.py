import discord, re

from discord.ext import commands
from discord.ext.commands import has_any_role, CheckFailure

from modules.core.database import Database

class AnimeClub(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	def is_anime_club_server(ctx):
		return ctx.guild.id == 254864526069989377

	@commands.group(pass_context=True, aliases=['sced', 'sc'])
	@commands.check(is_anime_club_server)
	async def schedule(self, ctx):
		await ctx.trigger_typing()
		if ctx.invoked_subcommand is None:
			await self.show_shcedule(ctx, wed=True, sat=True)

	@schedule.command(pass_context=True, aliases=['sat', 'SAT', 'Sat', 'Saturday'])
	async def saturday(self, ctx):
		await self.show_shcedule(ctx, sat=True)

	@schedule.command(pass_context=True, aliases=['wed', 'WED', 'Wed', 'Wednesday'])
	async def wednesday(self, ctx):
		await self.show_shcedule(ctx, wed=True)

	@schedule.command(pass_context=True, name="set")
	@has_any_role(494979840470941712, 259557922726608896)
	async def set_(self, ctx, *args):
		if not args:
			await ctx.send('Invalid command. Try `>schedule set sat <show1><show2><show3>` (the < and > are needed). To set wednesday, use <timeX: showX> in the command.')
		elif args[0] in ['wed', 'WED', 'Wed', 'Wednesday', 'wednesday']:
			await self.set_wed(ctx, args[1:])
		elif args[0] in ['sat', 'SAT', 'Sat', 'Saturday', 'saturday']:
			await self.set_sat(ctx, args[1:])
		else:
			await ctx.send('Invalid command. Try `>schedule set sat <show1><show2><show3>` (the < and > are needed). To set wednesday, use <timeX: showX> in the command.')

	async def set_sat(self, ctx, args):
		data = re.findall('<[^>]*>',' '.join(args))
		for i in range(0,3):
			if not data[i]:
				await ctx.send('Error setting saturday schedule!')
				return
			data[i] = str(6+i) + '-' + str(7+i) + "p: " + data[i][1:-1:1]
		data.append('9-11p: Social Time')
		res = await Database.storage_update_one({'id': 'schedule'}, {'$set': {'saturday': data}})
		if not res:
			await ctx.send('Error setting Saturday schedule!')
		else:
			await ctx.send('Saturday schedule has been updated!')


	async def set_wed(self, ctx, args):
		data = re.findall('<[^:]*:[^>]*>',' '.join(args))
		data = [e[1:-1:1] for e in data]
		res = await Database.storage_update_one({'id': 'schedule'}, {'$set': {'wednesday': data}})
		if not res:
			await ctx.send('Error setting Wednesday schedule!')
		else:
			await ctx.send('Wednesday schedule has been updated!')

	async def show_shcedule(self, ctx, wed=False, sat=False):
		if not wed and not sat:
			return
		else:
			embed=discord.Embed(description="Club Schedule", color=0xd31f28)
			embed.set_thumbnail(url="https://files.catbox.moe/9dsqp5.png")
			data = await Database.storage_find_one({'id': 'schedule'})
			if sat:
				if data['saturday']:
					embed.add_field(name="Saturday", value='\n'.join(data['saturday']), inline=False)
				else:
					embed.add_field(name="Saturday", value="<>", inline=False)
			if wed:
				if data['wednesday']:
					embed.add_field(name="Wednesday", value='\n'.join(data['wednesday']), inline=True)
				else:
					embed.add_field(name="Wednesday", value="<>", inline=False)
			await ctx.send(embed=embed)