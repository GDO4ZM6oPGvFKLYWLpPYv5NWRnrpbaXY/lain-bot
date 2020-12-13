import logging, discord, datetime, os, openpyxl
logger = logging.getLogger(__name__)

from discord.ext import commands
from discord.ext.commands import has_any_role
from dateutil import parser
from openpyxl import load_workbook
from tempfile import NamedTemporaryFile

from modules.core.resources import Resources

class AnimeClub(commands.Cog):

	def __init__(self, bot):
		self.bot = bot

	def is_anime_club_server(ctx):
		return ctx.guild.id in [254864526069989377, 259896980308754432]

	async def cog_command_error(self, ctx, err):
		logger.exception("Error during Anime Club command.")
		try:
			await ctx.send('error!', file=discord.File(os.getcwd() + '/assets/lain_err_sm.png'))
		except:
			pass

	@commands.group(aliases=['sced', 'sc'])
	@commands.check(is_anime_club_server)
	async def schedule(self, ctx):
		await ctx.trigger_typing()
		if ctx.invoked_subcommand is None:
			if ctx.message.content in ['>sc', '>sced']:
				await self.show_shcedule(ctx, wed=True, sat=True)
			else:
				await ctx.send('Bad usage. Try `>sc` `>sc wed` or `>sc wed future`. Can replace wed with sat as well')

	@schedule.group(aliases=['sat', 'SAT', 'Sat', 'Saturday'])
	async def saturday(self, ctx):
		if ctx.invoked_subcommand is None:
			await self.show_shcedule(ctx, sat=True)

	@schedule.group(aliases=['wed', 'WED', 'Wed', 'Wednesday'])
	async def wednesday(self, ctx):
		if ctx.invoked_subcommand is None:
			await self.show_shcedule(ctx, wed=True)

	@schedule.command(name='all')
	async def all_both(self, ctx):
		await self.show_all_wed(ctx)
		await self.show_all_sat(ctx)

	@saturday.command(name='all')
	async def all_sat(self,ctx):
		await self.show_all_sat(ctx)

	@wednesday.command(name='all')
	async def all_wed(self, ctx):
		await self.show_all_wed(ctx)

	@schedule.command(name='future')
	async def future_both(self, ctx):
		await self.show_all_wed(ctx, only_future=True)
		await self.show_all_sat(ctx, only_future=True)

	@saturday.command(name='future')
	async def future_sat(self,ctx):
		await self.show_all_sat(ctx, only_future=True)

	@wednesday.command(name='future')
	async def future_wed(self, ctx):
		await self.show_all_wed(ctx, only_future=True)

	@schedule.command(name="set")
	@has_any_role(494979840470941712, 259557922726608896, 260093344858767361) # admin, executive council
	async def set_(self, ctx, *args):
		if not args or args[0] not in ['sat', 'wed']:
			await ctx.send('Bad usage. Try `>sc set wed` or similar')

		if not ctx.message.attachments:
			await ctx.send('Provide an attachment by pressing the icon to the left of the input box and then doing the command in the message popup')

		k = 'Wednesday'
		n = 7
		if args[0] == 'sat':
			k = 'Saturday'
			n = 6
		
		with NamedTemporaryFile(delete=False, suffix='.xlsx') as tmp:
			await ctx.message.attachments[0].save(tmp.name)
			try:
				sched = extract_schedule(tmp.name, n)
			except Exception as e:
				await ctx.send(f"Failed to extract schedule from file.\n{e.message}")
				return
			res = await Resources.storage_col.update_one({'id': 'sched_v2'}, {'$set': {k: sched}})
			if not res:
				await ctx.send(f"Error setting {k} schedule!")
			else:
				await ctx.send(f"{k} schedules have been updated!")

	async def show_shcedule(self, ctx, wed=False, sat=False):
		if not wed and not sat:
			return
		else:
			embed=discord.Embed(description="Club Schedule", color=0xd31f28)
			embed.set_thumbnail(url="https://files.catbox.moe/9dsqp5.png")
			data = await Resources.storage_col.find_one({'id': 'sched_v2'})

			if sat:
				nxt_sat = next_day(day=5)
				lines = saturday_lines(data['Saturday'].get(str(nxt_sat)))
				if lines:
					embed.add_field(name=f"Saturday ({nxt_sat.month}/{nxt_sat.day})", value='\n'.join(lines), inline=False)
				else:
					embed.add_field(name=f"Saturday ({nxt_sat.month}/{nxt_sat.day})", value="*none*", inline=False)
			if wed:
				nxt_wed = next_day(day=2)
				lines = wednesday_lines(data['Wednesday'].get(str(nxt_wed)))

				if lines:
					embed.add_field(name=f"Wednesday ({nxt_wed.month}/{nxt_wed.day})", value='\n'.join(lines), inline=True)
				else:
					embed.add_field(name=f"Wednesday ({nxt_wed.month}/{nxt_wed.day})", value="*none*", inline=False)

			await ctx.send(embed=embed)

	async def show_all_wed(self, ctx, only_future=False):
		embed=discord.Embed(description="Wednesday Schedules", color=0xd31f28)
		embed.set_thumbnail(url="https://files.catbox.moe/9dsqp5.png")

		data = await Resources.storage_col.find_one({'id': 'sched_v2'})
		if 'Wednesday' not in data:
			embed.add_field(name='Unavailable', value='could not find Wednesday data')
		else:
			for meeting in data['Wednesday']:
				date = parser.parse(meeting)
				if only_future and date < next_day(day=2):
					continue
				lines = wednesday_lines(data['Wednesday'][meeting])
				if lines:
					embed.add_field(name=f"{date.month}/{date.day}", value='\n'.join(lines), inline=False)

		await ctx.send(embed=embed)

	async def show_all_sat(self, ctx, only_future=False):
		embed=discord.Embed(description="Saturday Schedules", color=0xd31f28)
		embed.set_thumbnail(url="https://files.catbox.moe/9dsqp5.png")

		data = await Resources.storage_col.find_one({'id': 'sched_v2'})
		if 'Saturday' not in data:
			embed.add_field(name='Unavailable', value='could not find Saturday data')
		else:
			for meeting in data['Saturday']:
				date = parser.parse(meeting)
				if only_future and date < next_day(day=5):
					continue
				lines = saturday_lines(data['Saturday'][meeting])
				if lines:
					embed.add_field(name=f"{date.month}/{date.day}", value='\n'.join(lines), inline=False)

		await ctx.send(embed=embed)

def wednesday_lines(data):
	lines = []
	if not data:
		return lines

	for showtime in data:
		if showtime['title']:
			lines.append(f"{showtime['start']}-{showtime['end']}: {showtime['title']}")
	return lines

def saturday_lines(data):
	lines = []
	if not data:
		return lines

	shows = {} # python 3.6+ dicts keep insertion order 🎉
	for showtime in data:
		if not showtime['title']:
			continue

		try:
			if showtime['title'].lower() == 'craptacular':
				lines.append('🎉💩 Craptacular 💩🎉')
				break
		except:
			pass

		if showtime['title'] in shows:
			shows[showtime['title']] += 1
		else:
			shows[showtime['title']] = 1

	n = 1
	for show in shows:
		lines.append(f"Slot {n}: {show} (x{shows[show]})") # order from dict
		n += 1

	return lines

def next_day(start=datetime.datetime.now(), day: int = 0, latest_same_day_hour: int = 21):
	"""Get date of next day of week following given date

	Args:
		start: date to search from. Defaults to datetime.datetime.now().
		day: day of the week: mon=0, ..., sun=6. Defaults to 0.
		latest_same_day_hour: latest hour to consider next day to be that day 
			i.e. if set to 6, anytime after 6 it will get the following week 
			while 6 or before will get that day. Defaults to 21.

	Returns:
		datetime.datetime: date with year. month, and day set
	"""
	start = Resources.timezone.localize(start)
	days_ahead = day - start.weekday()
	if days_ahead < 0:
		days_ahead += 7
	elif days_ahead == 0:
		if start.hour >= latest_same_day_hour:
			days_ahead = 7
	return datetime.datetime(start.year, start.month, start.day) + datetime.timedelta(days_ahead)

def extract_schedule(file, start_hour):
	class Time:
		def __init__(self, hour, min):
			self.hour = hour
			self.min = min

		def incr(self, min):
			hours = max(1, min // 60)
			if self.min + min >= 60:
				self.hour += hours
				self.min = self.min + min - (hours*60)
			else:
				self.min += min

		def __str__(self):
			return f"{self.hour}{':'+str(self.min) if self.min else ''}"
	
	wb = load_workbook(filename=file)
	sheet = wb.active
	data = {}
	# go through all rows starting form second (1-based indexing)
	for row in sheet.iter_rows(2):
		# ignore if date isn't 1st column element (0-based indexing here)
		if not isinstance(row[0].value, datetime.datetime):
			continue

		entries = []

		prev = row[1].value
		entry = {
			'title': prev,
			'start': str(start_hour),
			'end': ''
		}
		time = Time(start_hour, 0)
		# get showtime data
		for cell in row[2:]:
			time.incr(10)

			if isinstance(cell, openpyxl.cell.cell.MergedCell) or (cell.value == None and entry['title'] == None):
				continue

			entry['end'] = str(time)
			entries.append(entry)
			entry = {
				'title': cell.value,
				'start': str(time),
				'end': ''
			}
			prev == cell.value


		time.incr(10)
		entry['end'] = str(time)
		entries.append(entry)

		data[str(row[0].value)] = entries
	return data