import discord, os, random, asyncio, logging, statistics, html
from discord.ext import commands
from requests import HTTPError
logger = logging.getLogger(__name__)

from modules.anime.safebooru import Safebooru
from modules.anime.doujin import Doujin
from modules.anime.anilist2 import Anilist2
from modules.anime.vndb import Vndb

from modules.core.resources import Resources

from modules.services.anilist.enums import ScoreFormat, Status
from modules.services.models.user import UserStatus
from modules.services import Service

class Anime(commands.Cog, name="Weeb"):
	"""search anime, manga, vns, and more"""

	def __init__(self, bot):
		self.bot = bot

	async def cog_command_error(self, ctx, err):
		logger.exception("Error during >al command")
		if isinstance(err, discord.ext.commands.errors.CommandInvokeError):
			err = err.original
		try:
			if isinstance(err, discord.ext.commands.MissingPermissions):
				await ctx.send("You lack the needed permissions!")
			elif isinstance(err, Anilist2.AnilistError):
				if err.status == 404:
					await ctx.send('https://files.catbox.moe/b7drrm.jpg')
					await ctx.send('*no results*')
				else:
					await ctx.send(f"Query request failed\nmsg: {err.message}\nstatus: {err.status}")	
			elif isinstance(err, HTTPError):	
				await ctx.send(err.http_error_msg)
			else:
				await ctx.send('error!', file=discord.File(os.getcwd() + '/assets/lain_err_sm.png'))
		except:
			pass
		
	@commands.command()
	async def safebooru(self, ctx, tags):
		"""Look up images on safebooru"""
		channel = ctx.message.channel

		safebooruSearch = Safebooru.booruSearch(tags)

		safebooruImageURL = safebooruSearch[0]
		safebooruPageURL = safebooruSearch[1]
		safebooruTagsTogether = safebooruSearch[2]

		embed = discord.Embed(
			title = tags,
			description = 'Here\'s the picture you were looking for:',
			color = discord.Color.green(),
			url = safebooruPageURL
		)

		embed.set_image(url=safebooruImageURL)
		embed.set_footer(text=safebooruTagsTogether)

		await channel.send(embed=embed)

	@commands.group()
	async def doujin(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('Invalid doujin command passed...')

	@doujin.command()
	async def search(self, ctx):
		tags = str(ctx.message.content)[(len(ctx.prefix) + len('doujin search ')):]
		links = Doujin.tagSearch(tags)
		
		await ctx.trigger_typing()
		embed = discord.Embed(
			title = 'Results',
			color = discord.Color.red()
		)
		embed.set_thumbnail(url='https://e-hentai.org/favicon.png')

		if links != None:
			def check(reaction, user):
				return user == ctx.message.author and (str(reaction.emoji) == '1️⃣' or str(reaction.emoji) == '2️⃣' or str(reaction.emoji) == '3️⃣' or str(reaction.emoji) == '4️⃣' or str(reaction.emoji) == '5️⃣' or str(reaction.emoji) == '6️⃣' or str(reaction.emoji) == '7️⃣' or str(reaction.emoji) == '8️⃣' or str(reaction.emoji) == '9️⃣')
			
			size = len(links)
			if size == 0:
				await ctx.send('No results, try different tags')
				return
			
			i = 1
			for d in links:
				split = d.split('/')
				id = split[4]
				token = split[5]
				meta = Doujin.metaSearch(id, token)
				embed.add_field(name=str(i) + '. ' + meta['title'])
				i += 1
				if i == 10:
					break
			msg = await ctx.send(embed=embed)
			# add reaction(s)
			if size >= 1:
				await msg.add_reaction('1️⃣')
			if size >= 2:
				await msg.add_reaction('2️⃣')
			if size >= 3:
				await msg.add_reaction('3️⃣')
			if size >= 4:
				await msg.add_reaction('4️⃣')
			if size >= 5:
				await msg.add_reaction('5️⃣')
			if size >= 6:
				await msg.add_reaction('6️⃣')
			if size >= 7:
				await msg.add_reaction('7️⃣')
			if size >= 8:
				await msg.add_reaction('8️⃣')
			if size >= 9:
				await msg.add_reaction('9️⃣')

			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
			except asyncio.TimeoutError:
				await ctx.send('Took too long, try again')
			
			else:
				try:
					chose = links[str(reaction.emoji)[:1] - 1]
				except:
					await ctx.send('Invalid reaction, try again')
					return
				
				embed = discord.Embed(
					title = 'Not done yet lol',
					color = discord.Color.red(),
					url=chose
				)
				await ctx.send(embed=embed)

		else:
			await ctx.send('Error getting data')

	@commands.group()
	async def al(self, ctx):
		# anilist command group
		if ctx.invoked_subcommand is None:
			await ctx.send('Invalid anilist command passed...')


	@al.command()
	async def search(self, ctx):
		"""search for anime in anilist"""
		await ctx.trigger_typing()
		show = str(ctx.message.content)[(len(ctx.prefix) + len('al search ')):]
		# retrieve json file
		anilistResults = await Anilist2.aniSearch(Resources.session, show, isAnime=True)

		# parse out website styling
		desc = shorten(str(anilistResults['data']['anime']['description']))

		# make genre list look nice
		gees = str(anilistResults['data']['anime']['genres'])
		gees = gees.replace('\'', '')
		gees = gees.replace('[', '')
		gees = gees.replace(']', '')

		# embed text to output
		embed = discord.Embed(
			title = str(anilistResults['data']['anime']['title']['romaji']),
			description = desc,
			color = discord.Color.blue(),
			url = str(anilistResults['data']['anime']['siteUrl'])
		)

		embed.set_footer(text=gees)

		# images, check if valid before displaying
		if 'None' != str(anilistResults['data']['anime']['bannerImage']):
			embed.set_image(url=str(anilistResults['data']['anime']['bannerImage']))

		if 'None' != str(anilistResults['data']['anime']['coverImage']['large']):
			embed.set_thumbnail(url=str(anilistResults['data']['anime']['coverImage']['large']))

		# studio name and link to their AniList page
		try:
			embed.set_author(name=str(anilistResults['data']['anime']['studios']['nodes'][0]['name']), url=str(anilistResults['data']['anime']['studios']['nodes'][0]['siteUrl']))
		except IndexError:
			logger.error('empty studio name or URL')

		# if show is airing, cancelled, finished, or not released
		status = anilistResults['data']['anime']['status']

		if 'NOT_YET_RELEASED' not in status:
			embed.add_field(name='Score', value=str(anilistResults['data']['anime']['meanScore']) + '%', inline=True)
			embed.add_field(name='Popularity', value=str(anilistResults['data']['anime']['popularity']) + ' users', inline=True)
			if 'RELEASING' not in status:
				embed.add_field(name='Episodes', value=f"{anilistResults['data']['anime']['episodes']} x {anilistResults['data']['anime']['duration']} min", inline=False)

				# make sure season is valid
				if str(anilistResults['data']['anime']['seasonYear']) != 'None' and str(anilistResults['data']['anime']['season']) != 'None':
					embed.add_field(name='Season', value=str(anilistResults['data']['anime']['seasonYear']) + ' ' + str(anilistResults['data']['anime']['season']).title(), inline=True)

				# find difference in year month and days of show's air time
				try:
					air = True
					years = abs(anilistResults['data']['anime']['endDate']['year'] - anilistResults['data']['anime']['startDate']['year'])
					months = abs(anilistResults['data']['anime']['endDate']['month'] - anilistResults['data']['anime']['startDate']['month'])
					days = abs(anilistResults['data']['anime']['endDate']['day'] - anilistResults['data']['anime']['startDate']['day'])
				except TypeError:
					logger.error('Error calculating air time')
					air = False

				# get rid of anything with zero
				if air:
					tyme = str(days) + ' days'
					if months != 0:
						tyme += ', ' + str(months) + ' months'
					if years != 0:
						tyme += ', ' + str(years) + ' years'

					embed.add_field(name='Aired', value=tyme, inline=False)

		if (embed.fields):
			tmp = embed.fields[-1]
			embed.set_field_at(len(embed.fields)-1, name=tmp.name, value=tmp.value, inline=False)

		extra = await embedScores(ctx.guild, anilistResults["data"]["anime"]["id"], anilistResults["data"]["anime"]["idMal"], 'anime', 9, embed)

		msg = await ctx.send(embed=embed)

		if extra:
			def check(reaction, user):
				return user != msg.author and str(reaction.emoji) == '➕'

			await msg.add_reaction('➕')

			try:
				reaction, author = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
			except asyncio.TimeoutError:
				await msg.clear_reactions()
			else:
				await ctx.send(f"({str(anilistResults['data']['anime']['title']['romaji'])})", embed=extra)

	@al.command()
	async def manga(self, ctx):
		"""Search for manga in anilist"""
		await ctx.trigger_typing()
		comic = str(ctx.message.content)[(len(ctx.prefix) + len('al manga ')):]
		# retrieve json file
		anilistResults = await Anilist2.aniSearch(Resources.session, comic, isManga=True)

		# parse out website styling
		desc = shorten(str(anilistResults['data']['manga']['description']))

		# make genre list look nice
		gees = str(anilistResults['data']['manga']['genres'])
		gees = gees.replace('\'', '')
		gees = gees.replace('[', '')
		gees = gees.replace(']', '')

		# embed text to output
		embed = discord.Embed(
			title = str(anilistResults['data']['manga']['title']['romaji']),
			description = desc,
			color = discord.Color.blue(),
			url = str(anilistResults['data']['manga']['siteUrl'])
		)

		embed.set_footer(text=gees)
		embed.add_field(name = 'Format', value=str(anilistResults['data']['manga']['format']).title())

		# images, check if valid before displaying
		if 'None' != str(anilistResults['data']['manga']['bannerImage']):
			embed.set_image(url=str(anilistResults['data']['manga']['bannerImage']))

		if 'None' != str(anilistResults['data']['manga']['coverImage']['large']):
			embed.set_thumbnail(url=str(anilistResults['data']['manga']['coverImage']['large']))


		# if show is airing, cancelled, finished, or not released
		status = anilistResults['data']['manga']['status']

		if 'NOT_YET_RELEASED' not in status:
			embed.add_field(name='Score', value=str(anilistResults['data']['manga']['meanScore']) + '%', inline=True)
			embed.add_field(name='Popularity', value=str(anilistResults['data']['manga']['popularity']) + ' users', inline=True)
			if 'RELEASING' not in status:
				embed.add_field(name='Chapters', value=str(anilistResults['data']['manga']['chapters']), inline=False)
				# find difference in year month and days of show's air time
				try:
					air = True
					years = abs(anilistResults['data']['manga']['endDate']['year'] - anilistResults['data']['manga']['startDate']['year'])
					months = abs(anilistResults['data']['manga']['endDate']['month'] - anilistResults['data']['manga']['startDate']['month'])
					days = abs(anilistResults['data']['manga']['endDate']['day'] - anilistResults['data']['manga']['startDate']['day'])
				except TypeError:
					logger.error('Error calculating air time')
					air = False

				# get rid of anything with zero
				if air:
					tyme = str(days) + ' days'
					if months != 0:
						tyme += ', ' + str(months) + ' months'
					if years != 0:
						tyme += ', ' + str(years) + ' years'

					embed.add_field(name='Released', value=tyme, inline=False)

		extra = await embedScores(ctx.guild, anilistResults["data"]["manga"]["id"], anilistResults["data"]["manga"]["idMal"], 'manga', 9, embed)

		msg = await ctx.send(embed=embed)

		if extra:
			def check(reaction, user):
				return user != msg.author and str(reaction.emoji) == '➕'

			await msg.add_reaction('➕')

			try:
				reaction, author = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
			except asyncio.TimeoutError:
				await msg.clear_reactions()
			else:
				await ctx.send(f"({str(anilistResults['data']['manga']['title']['romaji'])})", embed=extra)

	@al.command()
	async def char(self, ctx):
		"""Search for a character on anilist"""
		c = str(ctx.message.content)[(len(ctx.prefix) + len('al char ')):]
		anilistResults = await Anilist2.aniSearch(Resources.session, c, isCharacter=True)

		embed = discord.Embed(
				title = str(anilistResults['data']['character']['name']['full']),
				color = discord.Color.blue(),
				url = str(anilistResults['data']['character']['siteUrl'])
			)

		# make alternative names look nice
		alts = str(anilistResults['data']['character']['name']['alternative'])
		alts = alts.replace('\'', '')
		alts = alts.replace('[', '')
		alts = alts.replace(']', '')

		image = str(anilistResults['data']['character']['image']['large'])
		if (image != 'None'):
			embed.set_image(url=image)

		try:
			embed.set_author(name=str(anilistResults['data']['character']['media']['nodes'][0]['title']['romaji']), url=str(anilistResults['data']['character']['media']['nodes'][0]['siteUrl']), icon_url=str(anilistResults['data']['character']['media']['nodes'][0]['coverImage']['medium']))
		except IndexError:
			logger.error('Character had empty show name or url, or image')

		embed.set_footer(text=alts)

		await ctx.send(embed=embed)

	@al.group()
	async def user(self, ctx, *args):
		if not args:
			await ctx.send("Wroong. Too lazy to update help rn")
		elif args[0] == 'profile':
			await self.profile(ctx, *args[1:])
		else:
			await _user_status(ctx, args, self.bot)

	async def profile(self, ctx, *user):
		await ctx.trigger_typing()
		search = {}
		if len(user):
			# username given
			user = user[0].rstrip()
			if user.startswith('<@!'):
				userLen = len(user)-1
				atUser = user[3:userLen]
				search = {'discord_id': atUser }
			elif user[len(user)-5]=="#":
				userId = ctx.guild.get_member_named(user).id
				if userId:
					# found in guild
					search = {'discord_id': str(userId) }
				else:
					# not found
					await ctx.send('Sorry. I could not find that user in this server.')
					return
			else:
				search = {'profile.name': user }
		else:
			#no username given -> retrieve message creator's info
			search = {'discord_id': str(ctx.message.author.id)}

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

			await ctx.send(embed=embed)
		else:
			# not found
			if 'profile.name' in search:
				await ctx.send('Sorry. I do not support searches on users not registered with me.')
			else:
				await ctx.send('Sorry. I could not find that user')

	@commands.group()
	async def vn(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('Invalid vndb command passed...')

	@vn.command()
	async def get(self, ctx):
		"""Lookup a visual novel on vndb"""
		# name of vn
		arg = str(ctx.message.content)[(len(ctx.prefix) + len('vn get ')):]
		try:
			# grab info from database
			vn = Vndb()
			r = vn.vn(arg.strip())
			r = r['items'][0]

			# assign variables
			title = r['title']
			link = 'https://vndb.org/v' + str(r['id'])

			try:
				desc = shorten(r['description'])
			except:
				desc = 'Empty Description'
			# ----
			try:
				score = str(r['rating'])
			except:
				score = 'Unknown'
			# ----
			try:
				votes = str(r['votecount'])
			except:
				votes = 'Unknown'
			# ----
			try:
				popularity = str(r['popularity'])
			except:
				popularity = 'Unknown'
			# ----
			try:
				released = r['released']
			except:
				released = 'Unknown'
			# ----
			try:
				length = {
					1 : 'Very Short (< 2 hours)',
					2 : 'Short (2 - 10 hours)',
					3 : 'Medium (10 - 30 hours)',
					4 : 'Long (30 - 50 hours)',
					5 : 'Very Long (> 50 hours)'
				}[r['length']]
			except:
				length = 'Unknown'
			# ----
			try:
				image = r['image']
			except:
				image = 'https://i.kym-cdn.com/photos/images/original/000/290/992/0aa.jpg'
			# ----
			try:
				screens = r['screens']
			except:
				screens = []
			# ----
			try:
				langs = str(r['languages']).replace('[', '').replace(']', '').replace('\'','')
			except:
				langs = 'Unknown'
			# ----
			try:
				platforms = str(r['platforms']).replace('[', '').replace(']', '').replace('\'','')
			except:
				platforms = 'Unknown'
			# NSFW images disabled by default
			nsfw = False

			# display info on discord
			embed = discord.Embed(
					title = title,
					description = desc,
					color = discord.Color.purple(),
					url = link
				)
			try:
				embed.set_author(name='vndb')
			except:
				pass

			# adding fields to embed
			if score != 'Unknown':
				embed.add_field(name='Score', value=score, inline=True)
			if votes != 'Unknown':
				embed.add_field(name='Votes', value=votes, inline=True)
			if popularity != 'Unknown':
				embed.add_field(name='Popularity', value=popularity, inline=True)
			if released != 'Unknown':
				embed.add_field(name='Released', value=released, inline=True)
			if length != 'Unknown':
				embed.add_field(name='Time To Complete', value=length, inline=True)
			if langs != 'Unknown':
				embed.add_field(name='Languages', value=langs, inline=True)
			if platforms != 'Unknown':
				embed.add_field(name='Platforms', value=platforms, inline=True)

			embed.set_footer(text='NSFW: {0}'.format({False : 'off', True : 'on'}[nsfw]))

			embed.set_thumbnail(url=image)

			# Filter out porn
			risky = []
			for pic in screens:
				if pic['nsfw']:
					risky.append(pic)

			for f in risky:
				screens.remove(f)

			# Post image
			if len(screens) >= 1:
				embed.set_image(url=random.choice(screens)['image'])

			await ctx.send(embed=embed)
		except Exception as e:
			logger.exception('Exception looking up VN')
			await ctx.send('VN not found (title usually has to be exact)')

	@vn.command()
	async def quote(self, ctx):
		"""Display a random visual novel quote"""
		q = Vndb()
		quote = q.quote()

		embed = discord.Embed(
					title = quote['quote'],
					color = discord.Color.purple()
				)

		embed.set_author(name=quote['title'], url='https://vndb.org/v' + str(quote['id']), icon_url=quote['cover'])

		await ctx.send(embed=embed)

def shorten(desc):
	# italic
	desc = desc.replace('<i>', '*')
	desc = desc.replace('</i>', '*')
	# bold
	desc = desc.replace('<b>', '**')
	desc = desc.replace('</b>', '**')
	# remove br
	desc = desc.replace('<br>', '')

	# keep '...' in
	desc = desc.replace('...', '><.')

	# limit description to three sentences
	sentences = findSentences(desc)
	if len(sentences) > 3:
		desc = desc[:sentences[2] + 1]

	# re-insert '...'
	desc = desc.replace('><', '..')

	return desc

def findSentences(s):
	return [i for i, letter in enumerate(s) if letter == '.' or letter == '?' or letter == '!']

def colorConversion(arg):
	colors = {
		"blue": discord.Color.blue(),
		"purple": discord.Color.purple(),
		"pink": discord.Color.magenta(),
		"orange": discord.Color.orange(),
		"red": discord.Color.red(),
		"green": discord.Color.green(),
		"gray": discord.Color.light_grey()
	}
	return colors.get(arg, discord.Color.teal())

def statusConversion(arg, listType):
	colors = {
		Status.CURRENT: "W",
		Status.PLANNING: "P",
		Status.COMPLETED: "C",
		Status.DROPPED: "D",
		Status.PAUSED: "H",
		Status.REPEATING: "R"
	}
	if listType == 'mangaList':
		colors[Status.CURRENT] = "R"
		colors[Status.REPEATING] = "RR"

	return colors.get(arg, "X")


async def embedScores(guild, anilistId, malId, listType, maxDisplay, embed):
		# get all users in db that are in this guild and have the show on their list
		userIdsInGuild = [str(u.id) for u in guild.members]

		users = [d async for d in Resources.user_col.find(
			{
				'discord_id': {'$in': userIdsInGuild},
				'status': { '$not': { '$eq': UserStatus.INACTIVE } },
				'$or': [
					{
						'$and': [{'service': 'anilist'}, {f"lists.{listType}.{anilistId}": {'$exists': True}}]
					},
					{
						'$and': [{'service': 'myanimelist'}, {f"lists.{listType}.{malId}": {'$exists': True}}]
					}
				]        
			},
			{
				'service': 1,
				'profile.name': 1,
				'profile.score_format': 1,
				'profile.favourites': 1,
				f"lists.{listType}.{anilistId}": 1,
				f"lists.{listType}.{malId}": 1
			}
			)
		]

		avg = calculateMean(users, malId, anilistId, listType)
		if avg:
			embed.add_field(name="Score (local)", value=f"{avg}%", inline=False)

		usrLen = len(users)
		for i in range(0, min(usrLen, maxDisplay-1)):
			userScoreEmbeder(users[i], anilistId if users[i]['service'] == 'anilist' else malId, listType, embed)

		# either load last or say there are '+XX others'
		if usrLen == maxDisplay:
			userScoreEmbeder(users[maxDisplay-1], anilistId if users[maxDisplay-1]['service'] == 'anilist' else malId, listType, embed)
			return None
		elif usrLen > maxDisplay:
			embed.add_field(name='+'+str(usrLen-maxDisplay+1)+' others', value="...", inline=True)
			extraEmbed = discord.Embed(color=discord.Color.blue())
			for i in range(maxDisplay-1, usrLen):
				userScoreEmbeder(users[i], anilistId if users[i]['service'] == 'anilist' else malId, listType, extraEmbed)
			return extraEmbed
		else:
			return None

def userScoreEmbeder(user, showID, listType, embed):
	entry = user['lists'][listType][str(showID)]
	status = statusConversion(entry['status'], listType)
	isFav = bool(user['profile']['favourites'].get(str(showID)))
	
	score = entry['score']
	if not score or score == 0:
		embed.add_field(name=user['profile']['name'], value=f"No Score ({status}){'⭐' if isFav else ''}", inline=True)
	else:
		embed.add_field(name=user['profile']['name'], value=f"{ScoreFormat(user['profile']['score_format']).formatted_score(score)} ({status}){'⭐' if isFav else ''}", inline=True)


def calculateMean(users, malId, anilistId, listType):
	scores = []
	for user in users:
		entry = user['lists'][listType][str(anilistId if user['service'] == 'anilist' else malId)]
		score = ScoreFormat(user['profile']['score_format']).normalized_score(entry['score'])
		if score:
			scores.append(score)

	if not scores:
		return None

	mean = statistics.fmean(scores)
	mean = round(mean, 2)

	return mean

def limitLength(lst):
	orgLen = len('\n'.join(lst))
	if orgLen <= 1024:
		return lst
	   
	lst.append('+#### others!')
	tLen = len('\n'.join(lst))
	lst = lst[:-1]
	numRemoved = 0
	lenRemoved = 0
	for i in reversed(range(len(lst))):
		lenRemoved += len(lst[i]) + 1
		numRemoved += 1
		del lst[i]
		if tLen - lenRemoved <= 1024:
			break

	lst.append('+' + str(numRemoved) + ' others!')
	return lst

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
		user = user[0].rstrip()
		if user.startswith('<@!'):
			userLen = len(user)-1
			atUser = user[3:userLen]
			search = {'discord_id': atUser }
		elif user[len(user)-5]=="#":
			userId = ctx.guild.get_member_named(user).id
			if userId:
				# found in guild
				search = {'discord_id': str(userId) }
			else:
				# not found
				await ctx.send('Sorry. I could not find that user in this server.')
				return None
		else:
			search = {'profile.name': user }
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

	await ctx.trigger_typing()

	user = None
	status = args[0]
	if len(args) > 1:
		user = args[1]

	kind = 'anime'

	if status == 'watching':
		status = Status.CURRENT
	if status == 'rewatching':
		status = Status.REPEATING
	if status == 'reading':
		kind = 'manga'
		status = Status.CURRENT

	if status not in [Status.CURRENT, Status.REPEATING, Status.COMPLETED, Status.DROPPED, Status.PAUSED, Status.PLANNING]:
		return await ctx.send("Bad usage: Unknown status.")

	statuses = [status]

	if status == Status.CURRENT:
		statuses.append(Status.REPEATING)
	if status == Status.REPEATING:
		statuses.append(Status.CURRENT)

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