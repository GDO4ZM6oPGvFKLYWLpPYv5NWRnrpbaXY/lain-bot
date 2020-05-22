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

	@bot.command(pass_context=True)
	async def anilist(ctx, param, show):
		if 'search' in param:
			# retrieve json file
			anilistResults = Anilist.aniSearch(show)

			# parse out website styling
			desc = str(anilistResults['data']['Media']['description'])
			# make italic
			desc = desc.replace('<i>', '*')
			desc = desc.replace('</i>', '*')
			# remove br
			desc = desc.replace('<br>', '')

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
			embed.set_image(url=str(anilistResults['data']['Media']['coverImage']['large']))
			#embed.set_thumbnail(url='')
			#embed.set_author(name='Author Name', icon_url='')
			await ctx.send(embed=embed)

