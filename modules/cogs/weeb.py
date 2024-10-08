import discord, os, random, asyncio, logging, statistics, html
from discord.ext import commands
from discord import app_commands
from requests import HTTPError
logger = logging.getLogger(__name__)

from modules.queries.anime.safebooru import Safebooru
from modules.queries.anime.doujin import Doujin
from modules.queries.anime.anilist2 import Anilist2
from modules.queries.anime.vndb import Vndb

from modules.core.resources import Resources

from modules.services.anilist.enums import ScoreFormat, Status
from modules.services.models.user import UserStatus
from modules.services import Service

class Weeb(commands.Cog, name="Weeb"):
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
			elif isinstance(err, discord.ext.commands.errors.MissingRequiredArgument):
				await ctx.send("Missing arguments!")
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
		
	@commands.hybrid_command()
	async def safebooru(self, ctx, *, tags):
		"""look up images on safebooru"""

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

		await ctx.send(embed=embed)

	@app_commands.command()
	async def doujin(self, interaction, tags: str):
		"""look up doujin"""
		await interaction.response.defer()
		links = Doujin.tagSearch(tags)
		
		embed = discord.Embed(
			title = 'Results',
			color = discord.Color.red()
		)
		embed.set_thumbnail(url='https://e-hentai.org/favicon.png')

		rxn = ['1️⃣','2️⃣','3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣']

		if links != None:
			def check(reaction, user):
				return user.id == interaction.user.id and str(reaction.emoji) in rxn
			
			size = len(links)
			if size == 0:
				await interaction.followup.send(content='No results, try different tags')
				return
			
			i = 1
			for d in links:
				split = d.split('/')
				id = split[4]
				token = split[5]
				meta = Doujin.metaSearch(id, token)
				embed.add_field(name=str(i) + '. ' + meta['title'], value='')
				i += 1
				if i == 10:
					break
			await interaction.followup.send(embed=embed)
			msg = await interaction.original_response()

			# add reaction(s)
			if size >= 1:
				await msg.add_reaction(rxn[0])
			if size >= 2:
				await msg.add_reaction(rxn[1])
			if size >= 3:
				await msg.add_reaction(rxn[2])
			if size >= 4:
				await msg.add_reaction(rxn[3])
			if size >= 5:
				await msg.add_reaction(rxn[4])
			if size >= 6:
				await msg.add_reaction(rxn[5])
			if size >= 7:
				await msg.add_reaction(rxn[6])
			if size >= 8:
				await msg.add_reaction(rxn[7])
			if size >= 9:
				await msg.add_reaction(rxn[8])

			try:
				reaction, user = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
			except asyncio.TimeoutError:
				await msg.clear_reactions()
			else:
				await msg.clear_reactions()
				chose = links[rxn.index(str(reaction.emoji))]

				embed = discord.Embed(
					title = 'Not done yet lol',
					color = discord.Color.red(),
					url=chose
				)
				await interaction.followup.send(embed=embed)

		else:
			await interaction.followup.send(content='Error getting data')


	@commands.hybrid_command(aliases=['a'], usage="<search>")
	async def anime(self, ctx, *, title):
		"""search for anime"""

		# await ctx.trigger_typing()

		if not title:
			return await ctx.send("Please give me a show to search for")

		anilistResults = await Anilist2.aniSearch(Resources.session, title, isAnime=True)

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

	@app_commands.command(name="ln")
	async def slash_ln(self, interaction, title: str):
		"""search for light novel"""
		anilistResults = await Anilist2.aniSearch(Resources.session, title, isLN=True)

		embed, extra = await mangaLnSearchEmbed(interaction.guild, anilistResults, 'ln')

		await interaction.response.send_message(embed=embed)

		if extra:
			msg = await interaction.original_response()

			def check(reaction, user):
				return user != msg.author and str(reaction.emoji) == '➕'

			await msg.add_reaction('➕')

			try:
				reaction, author = await self.bot.wait_for('reaction_add', timeout=10.0, check=check)
			except asyncio.TimeoutError:
				await msg.clear_reactions()
			else:
				await interaction.followup.send(content=f"({str(anilistResults['data']['ln']['title']['romaji'])})", embed=extra)


	@commands.hybrid_command(aliases=['m'], usage="<search>")
	@app_commands.describe(
		title='manga title',
	)
	async def manga(self, ctx, *, title):
		"""search for manga"""

		# await ctx.trigger_typing()

		if not title:
			return await ctx.send("Please give me a manga to search for")

		anilistResults = await Anilist2.aniSearch(Resources.session, title, isManga=True)

		embed, extra = await mangaLnSearchEmbed(ctx.guild, anilistResults, 'manga')

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

	@commands.hybrid_command(aliases=['c'], usage="<search>")
	@app_commands.describe(
    	name='character from anime or manga',
    )
	async def char(self, ctx, *, name):
		"""search for a character"""

		if not name:
			return await ctx.send("Please give me a character to search for")

		anilistResults = await Anilist2.aniSearch(Resources.session, name, isCharacter=True)

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


	vn_group = app_commands.Group(name='vn', description="get info related to VNs")

	@vn_group.command()
	@app_commands.describe(name='title of vn',)
	async def get(self, interaction, name: str):
		"""lookup a visual novel on vndb"""

		try:
			# grab info from database
			vn = Vndb()
			r = vn.vn(name)
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

			await interaction.response.send_message(embed=embed)
		except Exception as e:
			logger.exception('Exception looking up VN')
			await interaction.response.send_message('VN not found (title usually has to be exact)')

	@vn_group.command()
	async def quote(self, interaction):
		"""display a random visual novel quote"""
		q = Vndb()
		quote = await q.quote()

		try:
			quote = await q.quote()
		except:
			return await interaction.response.send_message('Unable to retrieve quote')

		embed = discord.Embed(
					title = quote['quote'],
					color = discord.Color.purple()
				)

		embed.set_author(name=quote['title'], url='https://vndb.org/' + str(quote['id']), icon_url=quote['cover'])

		await interaction.response.send_message(embed=embed)


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

async def mangaLnSearchEmbed(guild, anilistResults, kind):
	# parse out website styling
	desc = shorten(str(anilistResults['data'][kind]['description']))

	# make genre list look nice
	gees = str(anilistResults['data'][kind]['genres'])
	gees = gees.replace('\'', '')
	gees = gees.replace('[', '')
	gees = gees.replace(']', '')

	# embed text to output
	embed = discord.Embed(
		title = str(anilistResults['data'][kind]['title']['romaji']),
		description = desc,
		color = discord.Color.blue(),
		url = str(anilistResults['data'][kind]['siteUrl'])
	)

	embed.set_footer(text=gees)
	embed.add_field(name = 'Format', value=str(anilistResults['data'][kind]['format']).title())

	# images, check if valid before displaying
	if 'None' != str(anilistResults['data'][kind]['bannerImage']):
		embed.set_image(url=str(anilistResults['data'][kind]['bannerImage']))

	if 'None' != str(anilistResults['data'][kind]['coverImage']['large']):
		embed.set_thumbnail(url=str(anilistResults['data'][kind]['coverImage']['large']))


	# if show is airing, cancelled, finished, or not released
	status = anilistResults['data'][kind]['status']

	if 'NOT_YET_RELEASED' not in status:
		embed.add_field(name='Score', value=str(anilistResults['data'][kind]['meanScore']) + '%', inline=True)
		embed.add_field(name='Popularity', value=str(anilistResults['data'][kind]['popularity']) + ' users', inline=True)
		if 'RELEASING' not in status:
			embed.add_field(name='Chapters', value=str(anilistResults['data'][kind]['chapters']), inline=False)
			# find difference in year month and days of show's air time
			try:
				air = True
				years = abs(anilistResults['data'][kind]['endDate']['year'] - anilistResults['data'][kind]['startDate']['year'])
				months = abs(anilistResults['data'][kind]['endDate']['month'] - anilistResults['data'][kind]['startDate']['month'])
				days = abs(anilistResults['data'][kind]['endDate']['day'] - anilistResults['data'][kind]['startDate']['day'])
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

	extra = await embedScores(guild, anilistResults["data"][kind]["id"], anilistResults["data"][kind]["idMal"], 'manga', 9, embed)
	return embed, extra