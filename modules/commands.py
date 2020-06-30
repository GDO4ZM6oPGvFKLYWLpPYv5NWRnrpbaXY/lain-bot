import youtube_dl
import ffmpeg
import discord
from discord.ext import commands
from discord.utils import get
import random
import sqlite3
import os

from .client import Client
from .config import Config
from .events import Events
from .safebooru import Safebooru
from .anilist import Anilist
from .vndb import Vndb
from .radio import Radio
from modules.fighting.fginfo import FgInfo
from .themes import Themes

bot = Client.bot

class Commands:

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
		embed.set_author(name='音無小鳥', url='https://www.project-imas.com/wiki/Kotori_Otonashi', icon_url='https://raw.githubusercontent.com/SigSigSigurd/kotori-san-bot/master/assets/search.png')
		embed.set_footer(text=safebooruTagsTogether)

		await channel.send(embed=embed)

	@bot.command(pass_context=True)
	async def serverID(ctx): #returns the serverID, mainly for debug purposes
		await ctx.send('Server ID: '+str(Client.serverID))

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

	@bot.group()
	async def radio(ctx):
		if ctx.invoked_subcommand is None:
				await ctx.send('Invalid radio command passed...')

	@radio.command(pass_context=True)
	async def start(ctx):
		# r/a/dio link
		url = 'https://stream.r-a-d.io/main.mp3'
		await join(ctx, url)

	@radio.command(pass_context=True)
	async def info(ctx):
		r = Radio.information()
		try:
			# variables
			main = r['main']
			song = main['np']
			q = main['queue']
			djname = main['dj']['djname']
			bitrate = str(main['bitrate'])
			listeners = str(main['listeners'])

			embed = discord.Embed(
					title = 'R/a/dio Information',
					color = discord.Color.red(),
					url = 'https://r-a-d.io/'
				)

			# now playing
			embed.add_field(name='Now Playing', value=song, inline=False)

			# queued songs
			i = 1
			out = ''
			for s in q:
				out += str(i) + '. ' + s['meta'] + '\n'
				i += 1
			embed.add_field(name='Queue', value=out, inline=False)

			embed.set_footer(text='DJ: {0}, Listeners: {1}, Bitrate: {2}'.format(djname, listeners, bitrate))

			await ctx.send(embed=embed)
		except:
			await ctx.send('Error retrieving data')
	
	@bot.command(pass_context=True)
	async def stop(ctx):
		try:
			channel = ctx.author.voice.channel
			voice = get(bot.voice_clients, guild=ctx.guild)

			if voice and voice.is_connected():
				await voice.disconnect()
			else:
				await ctx.send('Not connected to a voice channel')
		except AttributeError as a:
			print(a)
			await ctx.send('Not in a voice channel')
		except Exception as e:
			print(e)
			await ctx.send('Unexpected error')

	
	@bot.command(pass_context=True)
	async def op(ctx, num):
		# 1 = opening
		t = 1
		build = parse(ctx, num)

		# show to search for
		show = build['show']
		# which opening to pick
		num = build['num']

		await ctx.send(show + ' ' + num)

		# first get list of openings from openings.moe
		songs = Themes.openingsMoe()

		if show == '':
			pick = random.choice(songs)
			show = pick['source']
			select = pick['title']
		else:
			select = 'Opening ' + num
		
		# anilist data
		anime = Anilist.aniSearch(show)

		# assign variables
		try:
			english = str(anime['data']['Media']['title']['english'])
			romaji = str(anime['data']['Media']['title']['romaji'])
			showUrl = anime['data']['Media']['siteUrl']
			showPic = anime['data']['Media']['coverImage']['extraLarge']
			year = anime['data']['Media']['startDate']['year']
			mal = str(anime['data']['Media']['idMal'])
		except:
			await ctx.send('Invalid show')

		# get rid of null returns
		if english == 'None':
			english = romaji
		elif romaji == 'None':
			romaji == english
		
		parts = Themes.search(english.lower(), romaji.lower(), show, select, songs)
		if parts['found']:
			embed = discord.Embed(
					title = parts['big'],
					color = discord.Color.orange(),
					url = parts['video']
				)
			
			embed.set_author(name=parts['title'], url=showUrl, icon_url=showPic)
			embed.set_footer(text=parts['op/ed'], icon_url='https://openings.moe/assets/logo/512px.png')
			await ctx.send(embed=embed)
			
			await join(ctx, parts['video'])
		else:
			try:
				parts = Themes.themesMoe(year, select, mal, t, num)
				big = num
				embed = discord.Embed(
						title = parts['name'],
						color = discord.Color.orange(),
						url = parts['video']
				)
				embed.set_author(name=romaji, url=showUrl, icon_url=showPic)
				embed.set_footer(text=select, icon_url='https://external-content.duckduckgo.com/ip3/themes.moe.ico')
				await ctx.send(embed=embed)
				
				await join(ctx, parts['video'])
			except Exception as e:
				print(e)
				await ctx.send('Show not found in database')

	@bot.command(pass_context=True)
	async def ed(ctx, num):
		# 2 = ending
		t = 2
		build = parse(ctx, num)

		# show to search for
		show = build['show']
		# which ending to pick
		num = build['num']

		# first get list of openings from openings.moe
		songs = Themes.openingsMoe()

		if show == '':
			pick = random.choice(songs)
			show = pick['source']
			select = pick['title']
		else:
			select = 'Ending ' + num

		# anilist data
		anime = Anilist.aniSearch(show)

		# search for ED
		try:
			english = str(anime['data']['Media']['title']['english'])
			romaji = str(anime['data']['Media']['title']['romaji'])
			showUrl = anime['data']['Media']['siteUrl']
			showPic = anime['data']['Media']['coverImage']['extraLarge']
			year = anime['data']['Media']['startDate']['year']
			mal = str(anime['data']['Media']['idMal'])
		except:
			await ctx.send('Invalid show')

		# get rid of null returns
		if english == 'None':
			english = romaji
		elif romaji == 'None':
			romaji == english
		
		parts = Themes.search(english, romaji, show, select, songs)
		if parts['found']:
			embed = discord.Embed(
					title = parts['big'],
					color = discord.Color.orange(),
					url = parts['video']
				)
			
			embed.set_author(name=parts['title'], url=showUrl, icon_url=showPic)
			embed.set_footer(text=parts['op/ed'], icon_url='https://openings.moe/assets/logo/512px.png')
			await ctx.send(embed=embed)
			
			await join(ctx, parts['video'])
		else:
			try:
				parts = Themes.themesMoe(year, select, mal, t, num)
				big = num
				embed = discord.Embed(
						title = parts['name'],
						color = discord.Color.orange(),
						url = parts['video']
				)
				embed.set_author(name=romaji, url=showUrl, icon_url=showPic)
				embed.set_footer(text=select, icon_url='https://external-content.duckduckgo.com/ip3/themes.moe.ico')
				await ctx.send(embed=embed)
				
				await join(ctx, parts['video'])
			except Exception as e:
				print(e)
				await ctx.send('Show not found in database')

	@bot.group()
	async def xiii(ctx):
		if ctx.invoked_subcommand is None:
			await ctx.send('Invalid xiii command passed...')

	@xiii.command(pass_context=True)
	async def fd(ctx, char, move):
		channel = ctx.message.channel

		frames = FgInfo.searchFd("xiii", char, move)
		movename = frames["Command"][0]
		startup = frames["Startup"]
		active = frames["Active"]
		recovery = frames["Recovery"]
		try:
			hit = frames["Hit"]
		except:
			hit = "null"
		try:
			block = frames["Block"]
		except:
			block = "null"
		try:
			notes = frames["Notes"]
		except:
			notes = "null"
		try:
			blockstun = frames["Blockstun"]
		except:
			blockstun = "null"
		try:
			hitstun = frames["Hitstun"]
		except:
			hitstun = "null"

		embed = discord.Embed(
			title = "Frame data for "+movename+" of "+char.capitalize()
		)

		embed.add_field(name='Startup Frames:', value=startup, inline=True)
		embed.add_field(name='Active Frames:', value=active, inline=True)
		embed.add_field(name='Recovery Frames:', value=recovery, inline=True)
		if hit != "null":
			embed.add_field(name='Hit Advantage:', value=hit, inline=True)
		if block != "null":
			embed.add_field(name='Block Advantage:', value=block, inline=True)
		if hitstun != "null":
			embed.add_field(name='Hitstun:', value=hitstun, inline=True)
		if blockstun != "null":
			embed.add_field(name='Blockstun:', value=blockstun, inline=True)
		if notes != "null":
			embed.add_field(name='Notes:', value=notes, inline=True)

		await channel.send(embed=embed)

	@xiii.command(pass_context=True)
	async def char(ctx, char):
		channel = ctx.message.channel
		info = FgInfo.searchChar("xiii", char)

		name = info["Name"]
		charimage = info["Image"]
		bio = info["Bio"]
		gameplay = info["Gameplay"]
		dreamcancel = info["DreamCancel"]
		shoryuken = info["Shoryuken"]

		embed = discord.Embed(
			title = name,
		)

		embed.set_image(url=charimage)
		embed.add_field(name='Biography:', value=bio, inline=False)
		embed.add_field(name='Gameplay:', value=gameplay, inline=False)
		embed.add_field(name='Dream Cancel Wiki:', value=dreamcancel, inline=False)
		embed.add_field(name='Shoryuken Wiki:', value=shoryuken, inline=False)

		await channel.send(embed=embed)

	@xiii.command(pass_context=True)
	async def game(ctx):
		channel = ctx.message.channel

		embed = discord.Embed(
			title = "The King of Fighters XIII"
		)
		embed.set_image(url="https://dreamcancel.com/wiki/images/0/04/KOF_XIII_Logo.png")
		embed.add_field(name="Gameplay", value="King of Fighters XIII is the latest entry in the KOF series. While it resembles XII graphically, all of XII's new systems (clash, critical counter, guard attack) have been removed. The developers stated that their concept for the game was \"KOF-ism,\" so many classic KOF systems return, such as guard cancel rolls and guard cancel attacks. Hyperdrive mode is modeled on 2002's BC mode, while Max Cancels resemble XI's Dream Cancels. Finally, new to the series are EX moves (more powerful special moves costing one bar) and Drive Cancels (canceling from one special to another.)", inline=False)
		embed.add_field(name="Steam Store", value="https://store.steampowered.com/app/222940/THE_KING_OF_FIGHTERS_XIII_STEAM_EDITION/", inline=False)
		embed.add_field(name="Fanatical Store", value="https://www.fanatical.com/en/game/the-king-of-fighters-xiii-steam-edition", inline=False)
		embed.add_field(name="GMG", value="https://www.greenmangaming.com/games/the-king-of-fighters-xiii-steam-edition-pc/", inline=False)
		embed.add_field(name="Note", value="This command will be updated down the line to check for sales, and it will be able to automatically post sales", inline=False)

		await channel.send(embed=embed)

	@bot.command(pass_context=True)
	async def botChannel(ctx):
		serverID = str(ctx.guild.id)
		channelID = str(ctx.channel.id)
		Config.cfgUpdate(serverID, "Bot Channel", channelID)
		await ctx.send("Bot channel successfully updated to here!")

	@bot.command(pass_context=True)
	async def botWhere(ctx):
		serverID = str(ctx.guild.id)
		# result = Config.cfgRead(serverID, "Bot Channel")
		await ctx.send(Config.cfgRead(serverID, "Bot Channel"))

# join a voice channel and play link
async def join(ctx, url):
	global voice
	try:
		# get voice channel
		channel = ctx.author.voice.channel
		if channel != None:
			# join channel
			voice = get(bot.voice_clients, guild=ctx.guild)
			
			if voice and voice.is_connected():
				# play music
				Radio.players[ctx.guild.id] = voice
				
			else:
				voice = await channel.connect()
			
			voice.play(discord.FFmpegPCMAudio(url), after=lambda e: print('Player error: %s' % e) if e else None)
	except AttributeError as a:
		print(a)
		await ctx.send('User is not in a channel.')
	except Exception as e:
		print(e)
		await ctx.send('Unexpected error')

# helper functions for vn and anilist search
def parse(ctx, num):
		# determine which op/ed should be played
		show = ''
		try:
			int(num[0])
			# get show name
			show = str(ctx.message.content)[(len(ctx.prefix) + len('op ' + str(num) + ' ')):]
		except ValueError as v:
			print(v)
			if len(num) >= 2:	
				num = '1'
				show = str(ctx.message.content)[(len(ctx.prefix) + len('op ')):]
				#await ctx.send('Choose which OP you want to play first (1, 2, 3...)')
		except IndexError as f:
			print(f)
		
		return {'show' : show, 'num' : num}

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
