import discord
from discord.ext import commands
import random

from modules.core.client import Client
from modules.config.user import User
from modules.anime.safebooru import Safebooru
from modules.anime.anilist import Anilist
from modules.anime.vndb import Vndb

bot = Client.bot

class Anime(commands.Cog):

	@bot.command(pass_context=True)
	async def safebooru(ctx, tags): #looks up images on safebooru

		channel = ctx.message.channel

		safebooruSearch = Safebooru.booruSearch(tags)

		safebooruImageURL = safebooruSearch[0]
		safebooruPageURL = safebooruSearch[1]
		safebooruTagsTogether = safebooruSearch[2]

		embed = discord.Embed(
			title = tags,
			description = 'Is this what you were looking for, producer?',
			color = discord.Color.green(),
			url = safebooruPageURL
		)

		embed.set_image(url=safebooruImageURL)
		embed.set_author(name='音無小鳥', url='https://www.project-imas.com/wiki/Kotori_Otonashi', icon_url='https://raw.githubusercontent.com/SigSigSigurd/kotori-san-bot/master/assets/search.jpg')
		embed.set_footer(text=safebooruTagsTogether)

		await channel.send(embed=embed)

	@bot.group()
	async def al(ctx):
		# anilist command group
		if ctx.invoked_subcommand is None:
			await ctx.send('Invalid anilist command passed...')


	@al.command(pass_context=True)
	async def search(ctx):
		show = str(ctx.message.content)[(len(ctx.prefix) + len('al search ')):]
		# retrieve json file
		anilistResults = Anilist.aniSearch(show)
		showID = anilistResults["data"]["Media"]["id"]

		# parse out website styling
		desc = shorten(str(anilistResults['data']['Media']['description']))

		# make genre list look nice
		gees = str(anilistResults['data']['Media']['genres'])
		gees = gees.replace('\'', '')
		gees = gees.replace('[', '')
		gees = gees.replace(']', '')

		# embed text to output
		embed = discord.Embed(
			title = str(anilistResults['data']['Media']['title']['romaji']),
			description = desc,
			color = discord.Color.blue(),
			url = str(anilistResults['data']['Media']['siteUrl'])
		)

		embed.set_footer(text=gees)

		# images, check if valid before displaying
		if 'None' != str(anilistResults['data']['Media']['bannerImage']):
			embed.set_image(url=str(anilistResults['data']['Media']['bannerImage']))

		if 'None' != str(anilistResults['data']['Media']['coverImage']['large']):
			embed.set_thumbnail(url=str(anilistResults['data']['Media']['coverImage']['large']))

		# studio name and link to their AniList page
		try:
			embed.set_author(name=str(anilistResults['data']['Media']['studios']['nodes'][0]['name']), url=str(anilistResults['data']['Media']['studios']['nodes'][0]['siteUrl']))
		except IndexError:
			print('empty studio name or URL\n')

		for user in ctx.guild.members:
			try:
				alID = User.userRead(str(user.id), "alID")
				alName = User.userRead(str(user.id), "alName")
				if alID!=0:
					scoreResults = Anilist.scoreSearch(alID, showID)["data"]["MediaList"]["score"]
					statusResults = statusConversion(Anilist.scoreSearch(alID, showID)["data"]["MediaList"]["status"])
					if scoreResults==0:
						embed.add_field(name=alName, value="No Score ("+statusResults+")", inline=True)
					else:
						embed.add_field(name=alName, value=str(scoreResults)+"/10 ("+statusResults+")", inline=True)
			except:
				pass

		# if show is airing, cancelled, finished, or not released
		status = anilistResults['data']['Media']['status']

		if 'NOT_YET_RELEASED' not in status:
			embed.add_field(name='Score', value=str(anilistResults['data']['Media']['meanScore']) + '%', inline=True)
			embed.add_field(name='Popularity', value=str(anilistResults['data']['Media']['popularity']) + ' users', inline=True)
			if 'RELEASING' not in status:
				embed.add_field(name='Episodes', value=str(anilistResults['data']['Media']['episodes']), inline=False)

				# make sure season is valid
				if str(anilistResults['data']['Media']['seasonYear']) != 'None' and str(anilistResults['data']['Media']['season']) != 'None':
					embed.add_field(name='Season', value=str(anilistResults['data']['Media']['seasonYear']) + ' ' + str(anilistResults['data']['Media']['season']).title(), inline=True)

				# find difference in year month and days of show's air time
				try:
					air = True
					years = abs(anilistResults['data']['Media']['endDate']['year'] - anilistResults['data']['Media']['startDate']['year'])
					months = abs(anilistResults['data']['Media']['endDate']['month'] - anilistResults['data']['Media']['startDate']['month'])
					days = abs(anilistResults['data']['Media']['endDate']['day'] - anilistResults['data']['Media']['startDate']['day'])
				except TypeError:
					print('Error calculating air time')
					air = False

				# get rid of anything with zero
				if air:
					tyme = str(days) + ' days'
					if months != 0:
						tyme += ', ' + str(months) + ' months'
					if years != 0:
						tyme += ', ' + str(years) + ' years'

					embed.add_field(name='Aired', value=tyme, inline=True)


		await ctx.send(embed=embed)

	@al.command(pass_context=True)
	async def char(ctx):
		c = str(ctx.message.content)[(len(ctx.prefix) + len('al char ')):]
		anilistResults = Anilist.charSearch(c)

		embed = discord.Embed(
				title = str(anilistResults['data']['Character']['name']['full']),
				color = discord.Color.blue(),
				url = str(anilistResults['data']['Character']['siteUrl'])
			)

		# make alternative names look nice
		alts = str(anilistResults['data']['Character']['name']['alternative'])
		alts = alts.replace('\'', '')
		alts = alts.replace('[', '')
		alts = alts.replace(']', '')

		image = str(anilistResults['data']['Character']['image']['large'])
		if (image != 'None'):
			embed.set_image(url=image)

		try:
			embed.set_author(name=str(anilistResults['data']['Character']['media']['nodes'][0]['title']['romaji']), url=str(anilistResults['data']['Character']['media']['nodes'][0]['siteUrl']), icon_url=str(anilistResults['data']['Character']['media']['nodes'][0]['coverImage']['medium']))
		except IndexError:
			print('Character had empty show name or url, or image')

		embed.set_footer(text=alts)

		await ctx.send(embed=embed)

	@al.group(pass_context=True)
	async def user(ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('Invalid Anilist user command passed...')

	# al user
	@user.command()
	async def set(ctx, user):
		#try:
		User.userUpdate(str(ctx.message.author.id), "alName", user)
		try:
			userID = Anilist.userSearch(user)["data"]["User"]["id"]
			User.userUpdate(str(ctx.message.author.id), "alID", userID)
			await ctx.send("Updated AL username!")
		except:
			await ctx.send("Failed to update AL username!")

	# al user
	@user.command()
	async def profile(ctx):
		user = str(ctx.message.content)[(len(ctx.prefix) + len('al user profile ')):]
		# when the message contents are something like "@Sigurd#6070", converts format into "<@!user_id>"

		atLen = len(user)-5
		if user == "":
			try:
				user = User.userRead(str(ctx.message.author.id), "alName")
			except:
				user = None
		elif user.startswith("<@!"):
			userLen = len(user)-1
			atUser = user[3:userLen]
			try:
				user = User.userRead(str(atUser), "alName")
			except:
				user = None
		# re.findall(".+#[0-9]{4}", txt)
		elif user[atLen]=="#":
			for users in bot.users:
				usersSearch = users.name+"#"+users.discriminator
				if usersSearch == user:
					try:
						user = User.userRead(str(users.id), "alName")
					except:
						return None

		try:
			anilistResults = Anilist.userSearch(user)["data"]["User"]
		except:
			print(user)
			if user == None:
				await ctx.send("Error! Make sure you've set your profile using ``>al user set``!")
			else:
				await ctx.send("Error! Make sure you're spelling everything correctly!")

		color = colorConversion(anilistResults["options"]["profileColor"])

		embed = discord.Embed(
			title = anilistResults["name"],
			color = color,
			url = anilistResults["siteUrl"]
		)

		animeGenres = anilistResults["statistics"]["anime"]["genres"][0]["genre"]+", "+anilistResults["statistics"]["anime"]["genres"][1]["genre"]+", "+anilistResults["statistics"]["anime"]["genres"][2]["genre"]+", "+anilistResults["statistics"]["anime"]["genres"][3]["genre"]+", "+anilistResults["statistics"]["anime"]["genres"][4]["genre"]

		# core user fields
		embed.set_image(url=anilistResults["bannerImage"])
		embed.set_thumbnail(url=anilistResults["avatar"]["large"])
		embed.add_field(name="About:", value=str(anilistResults["about"]), inline=False)
		embed.set_footer(text="Last update: "+str(anilistResults["updatedAt"]))

		# anime fields
		embed.add_field(name="Anime count:", value=str(anilistResults["statistics"]["anime"]["count"]), inline=True)
		embed.add_field(name="Mean anime score:", value=str(anilistResults["statistics"]["anime"]["meanScore"])+"/100.00", inline=True)
		embed.add_field(name="Top anime genres:", value=animeGenres, inline=False)

		await ctx.send(embed=embed)

	@bot.group()
	async def mal(ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('Invalid MAL command passed...')

	@mal.group(pass_context=True)
	async def user(ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('Invalid MAL user command passed...')

	@user.command()
	async def search(ctx):
		await ctx.send("MAL WIP")

	@bot.group()
	async def vn(ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('Invalid vndb command passed...')

	@vn.command(pass_context=True)
	async def get(ctx):
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
			print(e)
			await ctx.send('VN no found')

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

def statusConversion(arg):
	colors = {
		"CURRENT": "W",
		"PLANNING": "P",
		"COMPLETED": "C",
		"DROPPED": "D",
		"PAUSED": "H",
		"REPEATING": "R"
	}
	return colors.get(arg, "X")
