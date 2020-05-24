import youtube_dl
import ffmpeg
import discord
from discord.ext import commands
import random
import sqlite3

from .client import Client
from .config import Config
from .events import Events
from .safebooru import Safebooru
from .anilist import Anilist

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
		desc = str(anilistResults['data']['Media']['description'])
		# make italic
		desc = desc.replace('<i>', '*')
		desc = desc.replace('</i>', '*')
		# make bold
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
		embed.set_author(name=str(anilistResults['data']['Media']['studios']['nodes'][0]['name']), url=str(anilistResults['data']['Media']['studios']['nodes'][0]['siteUrl']))

		# if show is airing, cancelled, finished, or not released
		status = anilistResults['data']['Media']['status']

		if 'NOT_YET_RELEASED' not in status:
			embed.add_field(name='Score', value=str(anilistResults['data']['Media']['meanScore']) + '%', inline=True)
			embed.add_field(name='Popularity', value=str(anilistResults['data']['Media']['popularity']) + ' users', inline=True)
			if 'RELEASING' not in status:
				embed.add_field(name='Episodes', value=str(anilistResults['data']['Media']['episodes']), inline=False)

				embed.add_field(name='Season', value=str(anilistResults['data']['Media']['seasonYear']) + ' ' + str(anilistResults['data']['Media']['season']).title(), inline=True)

				# find difference in year month and days of show's air time
				years = abs(anilistResults['data']['Media']['endDate']['year'] - anilistResults['data']['Media']['startDate']['year'])
				months = abs(anilistResults['data']['Media']['endDate']['month'] - anilistResults['data']['Media']['startDate']['month'])
				days = abs(anilistResults['data']['Media']['endDate']['day'] - anilistResults['data']['Media']['startDate']['day'])

				# get rid of anything with zero
				tyme = str(days) + ' days'
				if months != 0:
					tyme += ', ' + str(months) + ' months'
				if years != 0:
					tyme += ', ' + str(years) + ' years'

				embed.add_field(name='Aired', value=tyme, inline=True)

		await ctx.send(embed=embed)

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

# helper function for anilist search
def findSentences(s):
	return [i for i, letter in enumerate(s) if letter == '.' or letter == '?' or letter == '!']
