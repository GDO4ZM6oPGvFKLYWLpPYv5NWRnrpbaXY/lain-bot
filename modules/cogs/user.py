import discord, os, asyncio, logging, statistics, html
from discord.ext import commands
from discord import app_commands
from requests import HTTPError
logger = logging.getLogger(__name__)

from modules.core.resources import Resources

from modules.services.anilist.enums import ScoreFormat, Status
from modules.services.models.user import UserStatus
from modules.services import Service

from typing import Literal, Optional

class User(commands.GroupCog, name="user"):
	"""see info about registered users"""

	def __init__(self, bot):
		self.bot = bot

	async def cog_command_error(self, ctx, err):
		logger.exception(f"Error during >{__name__} command")
		if isinstance(err, discord.ext.commands.errors.CommandInvokeError):
			err = err.original
		try:
			await ctx.send('error!', file=discord.File(os.getcwd() + '/assets/lain_err_sm.png'))
		except:
			pass
		
	@commands.command()
	async def user(self, ctx, *args):
		if not args:
			await ctx.send("Wrong. Too lazy to update help rn")
		elif args[0] == 'profile':
			await _msg_cmd_profile(ctx, *args[1:])
		else:
			await _user_status(ctx, args, self.bot)


	@app_commands.command(name="profile")
	@app_commands.describe(user='the discord user to check (defaults to self)')
	async def slash_profile(self, interaction, user: Optional[discord.Member] = None):
		"""see user's' profile"""
		if not user:
			search = {'discord_id': str(interaction.user.id)}
		else:
			search = {'discord_id': str(user.id)}
		await _profile(interaction.response.send_message, search)

	@app_commands.command(name="manga")
	@app_commands.describe(user='the discord user to check (defaults to self)',)
	async def manga(self, interaction, status: Literal['reading', 'rereading', Status.COMPLETED, Status.DROPPED, Status.PAUSED, Status.PLANNING], user: Optional[discord.Member] = None):
		"""see the manga a user is reading, dropped, etc."""
		pass

	@app_commands.command(name="anime")
	@app_commands.describe(user='the discord user to check (defaults to self)',)
	async def anime(self, interaction, status: Literal['watching', 'rewatching', Status.COMPLETED, Status.DROPPED, Status.PAUSED, Status.PLANNING], user: Optional[discord.Member] = None):
		"""see the anime a user is watching, dropped, etc."""
		pass
	

async def _msg_cmd_profile(ctx, *user):
	# await ctx.trigger_typing()
	search = {}
	try:
		mention = ctx.message.mentions[0]
	except IndexError:
		mention = None

	if mention is not None:
		search = {'discord_id': str(mention.id) }
	elif len(user):
		search = {'profile.name': user }
	else:
		#no username given -> retrieve message creator's info
		search = {'discord_id': str(ctx.message.author.id)}

	return await _profile(ctx.send, search)

async def _profile(respond, search):
	# technically a user could register both anilist and myanimelist services
	# rn it'll just use what ever db query finds first
	search['service'] = {'$in': [Service.ANILIST, Service.MYANIMELIST]} 
	search['status'] = {'$in': [UserStatus.ACTIVE, UserStatus.CACHEONLY]}

	userData = await Resources.user_col.find_one(
		search,
		{
			'service': 1,
			'service_id': 1,
			'profile': 1,
			'lists.anime': 1
		}
	)
	if userData:
		# found
		embed = discord.Embed(
			title = userData['profile']['name'],
			color = discord.Color.teal(),
			url = Service(userData['service']).link(userData['service_id'])
		)

		animeGenres = ', '.join(userData['profile']['genres'])
		animeFavs = ', '.join(f for f in userData['profile']['favourites'].values())

		if len(animeFavs) > 1024:
			animeFavs = f"{animeFavs[:1021]}..."

		if userData['profile']["banner"]:
			embed.set_image(url=userData['profile']["banner"])
		if userData['profile']["avatar"]:
			embed.set_thumbnail(url=userData['profile']["avatar"])
		if userData['profile']['about']:
			v = html.unescape(str(userData['profile']['about']))
			if len(v) > 1024:
				v = f"{v[:1021]}..."
			embed.add_field(name="About:", value=v, inline=False)

		count = len([u for u in userData['lists']['anime'].values() if u['status'] in [Status.COMPLETED, Status.REPEATING]])
		embed.add_field(name="Anime completed:", value=f"{count}", inline=True)
		
		scores = [e['score'] for e in userData['lists']['anime'].values() if e['score']]
		if scores:
			mean = statistics.fmean(scores)
			mean = round(mean, 2)
			embed.add_field(name="Mean anime score:", value=ScoreFormat(userData['profile']['score_format']).formatted_score(mean), inline=True)

		if animeFavs:
			embed.add_field(name="Favourites:", value=animeFavs, inline=False)

		if animeGenres:
			embed.add_field(name="Top genres (by count):", value=animeGenres, inline=False)

		await respond(embed=embed)
	else:
		# not found
		if 'profile.name' in search:
			await respond('Sorry. I do not support searches on users not registered with me.')
		else:
			await respond('Sorry. I could not find that user')

def _limit_paginated(lst):
	pages = []
	hint = 'click + to view the others!'
	hint_len = len(hint)
	max_len = 1024 - hint_len - 1

	l = len('\n'.join(lst))
	if l <= 1024:
		return [lst]

	page = []
	for i in range(len(lst)):
		curr_len = len('\n'.join(page))
		if curr_len + len(lst[i]) + 1 <= max_len:
			page.append(lst[i])
		else:
			page.append(hint)
			pages.append(page)
			page = [lst[i]]
	pages.append(page)

	return pages

async def _user_get_status_lists(ctx, user, kind, statuses):
	search = {}
	if user:
		# username given
		if user.startswith('<@!'):
			userLen = len(user)-1
			atUser = user[3:userLen]
			search = {'discord_id': atUser }
		else:
			await ctx.send('Sorry. I could not find that user in this server.')
			return None
	else:
		#no username given -> retrieve message creator's info
		search = {'discord_id': str(ctx.message.author.id)}

	search['status'] = { '$not': { '$eq': UserStatus.INACTIVE } }

	userData = await Resources.user_col.find_one(
		search,
		{
			'service': 1,
			'service_id': 1,
			'profile': 1,
			f"lists.{kind}": 1
		}
	)

	data = {'user': None, 'lists': {}}
	for status in statuses:
		data['lists'][status] = []

	if userData:
		data['user'] = {
			'service': userData['service'],
			'service_id': userData['service_id'],
			'profile': userData['profile']
		}
		for e in userData['lists'][kind].values():
			if e['status'] in statuses:
				data['lists'][e['status']].append(e)
	else:
		# not found
		if 'profile.name' in search:
			await ctx.send('Sorry. I do not support searches on users not registered with me')
			await ctx.send('...yet')
			return None
		else:
			await ctx.send('Sorry. I do not have that user\'s info')
			return None

	for status in statuses:
		if status == Status.COMPLETED:
			data['lists'][status].sort(key=lambda e: e['score'], reverse=True)
		elif status == Status.DROPPED:
			def k(e):
				if kind == 'anime':
					return e['episode_progress']
				else:
					if e['chapter_progress']:
						return e['chapter_progress']
					else:
						return e['volume_progress']
			data['lists'][status].sort(key=k, reverse=True)
		else:
			data['lists'][status].sort(key=lambda e: e['title'])

	return data

async def _user_status(ctx, args, bot):
	if len(args) < 1:
		return await ctx.send("Bad usage: Try `>al user <status> <user>`. Ex `>al user dropped` to get your dropped list")

	# await ctx.trigger_typing()

	kind = None
	status = None
	user = None

	if args[0] == 'manga':
		kind = 'manga'
		status = args[1]
	else:
		kind = 'anime'
		status = args[0]

	if len(args) > 1:
		for i, arg in enumerate(args, start=1):
			arg = arg.rstrip()
			if arg.startswith('<@!'):
				user = arg
				break

	if status == 'watching':
		kind = 'anime'
		status = Status.CURRENT
	elif status == 'rewatching':
		kind = 'anime'
		status = Status.REPEATING
	elif status == 'reading':
		kind = 'manga'
		status = Status.CURRENT
	elif status == 'rereading':
		kind = 'manga'
		status = Status.REPEATING

	if status not in [Status.CURRENT, Status.REPEATING, Status.COMPLETED, Status.DROPPED, Status.PAUSED, Status.PLANNING]:
		return await ctx.send("Bad usage: Unknown status.")

	statuses = [status]

	if status == Status.CURRENT:
		statuses.append(Status.REPEATING)
	# if status == Status.REPEATING:
	# 	statuses.append(Status.CURRENT)

	data = await _user_get_status_lists(ctx, user, kind, statuses)

	if not data:
		return

	user_info = data['user']
	data = data['lists']

	stringed_data = {}

	for status in statuses:
		stringed_data[status] = []
		if status in [Status.CURRENT, Status.REPEATING, Status.DROPPED, Status.PAUSED]:
			for e in data[status]:
				s = f"• {e['title']} ({e['episode_progress' if kind == 'anime' else 'chapter_progress']}/{e['episodes' if kind == 'anime' else 'chapters'] if e['episodes' if kind == 'anime' else 'chapters'] else '-'})"
				stringed_data[status].append(s)
		elif status == Status.PLANNING:
			for e in data[status]:
				s = f"• {e['title']}"
				stringed_data[status].append(s)
		elif status == Status.COMPLETED:
			for e in data[status]:
				s = f"• {e['title']} ({ScoreFormat(user_info['profile']['score_format']).formatted_score(e['score'])})"
				stringed_data[status].append(s)

		stringed_data[status] = _limit_paginated(stringed_data[status])

	await _display_status_list(ctx, kind, user_info, stringed_data, 0, bot)

async def _display_status_list(ctx, kind, user_info, stringed_data, idx, bot):
	embed = discord.Embed(
		title = f"{user_info['profile']['name']}",
		description = '' if not idx else f"page {idx+1}",
		color = discord.Color.teal(),
		url = Service(user_info['service']).link(user_info['service_id'])
	)
	embed.set_thumbnail(url=user_info['profile']['avatar'])

	embed.set_image(url='https://files.catbox.moe/ixivqn.png') # mobile width fix

	has_next = False
	for status in stringed_data:
		try:
			d = stringed_data[status][idx]
		except:
			d = None
		embed.add_field(name=f"{kind.title()} {status.title()}", value='\n'.join(d) if d else '*None*', inline=False)
		try:
			has_next = bool(stringed_data[status][idx+1])
		except:
			pass

	msg = await ctx.send(embed=embed)

	if has_next:
		await msg.add_reaction('➕')

		def check(reaction, user):
			return user != msg.author and str(reaction.emoji) == '➕'

		try:
			reaction, author = await bot.wait_for('reaction_add', timeout=10.0, check=check)
		except asyncio.TimeoutError:
			await msg.clear_reactions()
		else:
			await msg.clear_reactions()
			await _display_status_list(ctx, kind, user_info, stringed_data, idx+1, bot)