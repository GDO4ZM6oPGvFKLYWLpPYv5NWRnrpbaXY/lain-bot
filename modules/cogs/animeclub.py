import discord, re, datetime, pytz

from discord.ext import commands
from discord.ext.commands import has_any_role, CheckFailure
from dateutil import parser

from modules.core.database import Database

tz = pytz.timezone('US/Central') 

class AnimeClub(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	def is_anime_club_server(ctx):
		return ctx.guild.id in [254864526069989377]

	async def cog_command_error(self, ctx, err):
		print(err)
		try:
			await ctx.send('error!', file=discord.File(os.getcwd() + '/assets/lain_err_sm.png'))
		except:
			pass

	@commands.group(aliases=['sced', 'sc'])
	@commands.check(is_anime_club_server)
	async def schedule(self, ctx):
		await ctx.trigger_typing()
		if ctx.invoked_subcommand is None:
			await self.show_shcedule(ctx, wed=True, sat=True)

	@schedule.command(aliases=['sat', 'SAT', 'Sat', 'Saturday'])
	async def saturday(self, ctx):
		await self.show_shcedule(ctx, sat=True)

	@schedule.group(aliases=['wed', 'WED', 'Wed', 'Wednesday'])
	async def wednesday(self, ctx):
		if ctx.invoked_subcommand is None:
			await self.show_shcedule(ctx, wed=True)

	@wednesday.command()
	async def all(self, ctx):
		await self.show_all_wed(ctx)

	@schedule.command(name="set")
	@has_any_role(494979840470941712, 259557922726608896) # admin, executive council
	async def set_(self, ctx, *args):
		if not args:
			await ctx.send('Invalid command. Try `>schedule set sat <show1><show2><show3>` (the < and > are needed). To set wednesday, use <timeX: showX> in the command.')
		elif args[0] in ['wed', 'WED', 'Wed', 'Wednesday', 'wednesday']:
			if args[1] == 'bulk':
				await self.set_wed_bulk(ctx)
			else:
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
		nxt_wed = next_wednesday()
		data = [e[1:-1:1] for e in data]
		res = await Database.storage_update_one({'id': 'schedule'}, {'$set': {'wednesday.'+str(nxt_wed): data}})
		if not res:
			await ctx.send('Error setting Wednesday schedule!')
		else:
			await ctx.send('Wednesday schedule for {}-{} has been updated!'.format(nxt_wed.month, nxt_wed.day))

	async def set_wed_bulk(self, ctx):
		lines = list(filter(None, ctx.message.content.split('\n')))[1:]
		update = {}
		date = str(to_date(lines[0][3:]))
		update[date] = []
		for e in lines[1:]:
			if e.startswith('d::'):
				date = str(to_date(e[3:]))
				update[date] = []
				continue
			update[date].append(e)
		res = await Database.storage_update_one({'id': 'schedule'}, {'$set': {'wednesday': update}})
		if not res:
			await ctx.send('Error setting Wednesday schedule!')
		else:
			await ctx.send('Wednesday schedules have been updated!')

	async def show_shcedule(self, ctx, wed=False, sat=False):
		if not wed and not sat:
			return
		else:
			embed=discord.Embed(description="Club Schedule", color=0xd31f28)
			embed.set_thumbnail(url="https://files.catbox.moe/9dsqp5.png")
			data = await Database.storage_find_one({'id': 'schedule'})
			if sat:
				if 'saturday' in data and data['saturday']:
					embed.add_field(name="Saturday", value='\n'.join(data['saturday']), inline=False)
				else:
					embed.add_field(name="Saturday", value="*none*", inline=False)
			if wed:
				nxt_wed = next_wednesday()
				if 'wednesday' in data and str(nxt_wed) in data['wednesday']:
					embed.add_field(name="Wednesday ({}/{})".format(nxt_wed.month, nxt_wed.day), value='\n'.join(data['wednesday'][str(nxt_wed)]), inline=True)
				else:
					embed.add_field(name="Wednesday ({}/{})".format(nxt_wed.month, nxt_wed.day), value="*none*", inline=False)
			await ctx.send(embed=embed)

	async def show_all_wed(self, ctx):
		embed=discord.Embed(description="Wednesday Schedule", color=0xd31f28)
		embed.set_thumbnail(url="https://files.catbox.moe/9dsqp5.png")
		data = await Database.storage_find_one({'id': 'schedule'})
		if 'wednesday' not in data:
			embed.add_field(name='Unavailable', value='unavailable')
		else:
			for meeting in data['wednesday']:
				date = parser.parse(meeting)
				embed.add_field(name="{}/{}".format(date.month, date.day), value='\n'.join(data['wednesday'][meeting]), inline=False)
		await ctx.send(embed=embed)

# get date of next wednesday with 10p being latest hour to be considered same wednesday
def next_wednesday(start=None):
	if not start:
		start = datetime.datetime.now()
	days_ahead = 2 - start.weekday()
	if days_ahead < 0:
		days_ahead += 7
	elif days_ahead == 0:
		if start.hour >= 22:
			days_ahead = 7
	return datetime.datetime(start.year, start.month, start.day, hour=22, tzinfo=tz) + datetime.timedelta(days_ahead)

# month-day-year string to datetimes
def to_date(s):
	t = s.split('-')
	return datetime.datetime(int(t[2]), int(t[0]), int(t[1]), hour=22, tzinfo=tz)