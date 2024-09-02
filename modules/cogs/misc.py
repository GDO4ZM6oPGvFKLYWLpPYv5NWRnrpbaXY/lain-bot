import discord, os, random, asyncio, logging, statistics, json, math, sys, traceback
from discord.ext import commands
from discord import app_commands
logger = logging.getLogger(__name__)

from modules.core.resources import Resources

from modules.services.anilist.enums import ScoreFormat, Status
from modules.services.models.user import UserStatus
from modules.services import Service

from typing import Literal, Optional

class Misc(commands.Cog, name="other"):
	"""Probably one-off or WIPs"""

	def __init__(self, bot):
		self.bot = bot

	async def cog_command_error(self, ctx, err):
		logger.exception("Error during command")
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
		
	@app_commands.command()
	@app_commands.describe(kind='anime or manga',)
	async def compatibility(self, interaction, kind: Optional[Literal['anime', 'manga']] = 'anime'):
		"""see your compatiblity with other registered users (pearson correlation coefficient)"""

		channel = interaction.channel
		guild = interaction.guild

		await interaction.response.send_message("I am slow at this for now. Just wait")

		user = await Resources.user_col.find_one(
			{'discord_id': str(interaction.user.id)},
			{
				'service': 1,
				'profile.name': 1,
				'profile.score_format': 1,
				f"lists.{kind}": 1,
			}
		)
		if not user:
			return await interaction.edit_original_response(content="Can't do compare. You're not registered")

		# get all users in db that are in this guild
		userIdsInGuild = [str(u.id) for u in guild.members if u.id != interaction.user.id]
		active_ids = [d async for d in Resources.user_col.aggregate(
				[
					{
						'$group': {
							'_id': None, 
							'data': {'$addToSet': {'discord_id': '$discord_id', 'status': '$status'}}
						}
					},
					{
						'$project': {
							'active': {
								'$filter': {
									'input': '$data',
									'as': 'item',
									'cond': {'$not': {'$eq': ['$$item.status', UserStatus.INACTIVE]}}
								}
							}
						}
					},
					{
						'$project': {
							'_id': 0,
							'active': '$active.discord_id'
						}
					}
				]
			)
		]
		common_ids = list(set(userIdsInGuild).intersection(set(active_ids[0]['active'])))

		scores = []
		async def _process(discord_id):
			u = await Resources.user_col.find_one(
				{
					'discord_id': discord_id,
				},
				{
					'service': 1,
					'profile.name': 1,
					'profile.score_format': 1,
					f"lists.{kind}": 1,
				}
			)
			scores.append((u['profile']['name'], _get_comp_score(user, u, kind)))

		Resources.al2mal2al.renew()

		await asyncio.gather(
			*[_process(discord_id) for discord_id in common_ids]
		)

		scores.sort(reverse=True, key=lambda e: e[1][0])

		# remove empty
		scores = [score for score in scores if score[1][0]]

		def chunkize(lst, size):
			for i in range(0, len(lst), size):
				yield lst[i:i+size]

		MAX_FIELDS = 24 # for discord, it's 25 but 24 formats into rows of 3 nicely
		page = 1
		pages = round(len(scores) / MAX_FIELDS)+1
		if scores:
			for subscores in chunkize(scores, MAX_FIELDS):
				title = f"{interaction.user.display_name}'s {kind} compatibility scores"
				if pages > 1:
					title += f" ({page}/{pages})"
				
				# embed text to output
				embed = discord.Embed(
					title = title,
					color = discord.Color.blue(),
				)

				for score in subscores:
					embed.add_field(name=score[0], value=f"{round(score[1][0], 1)}% ({score[1][1]})", inline=True)
				if page == 1:
					await interaction.edit_original_response(content=None, embed=embed)
				else:
					await interaction.followup.send(embed=embed)
				page += 1
		else:
			await interaction.edit_original_response(content="No compatibilities. Most likely didn't share any scores with anyone")

def _get_comp_score(u1, u2, kind):
	# https://en.wikipedia.org/wiki/Pearson_correlation_coefficient
	try:
		sf1 = ScoreFormat(u1['profile']['score_format'])
		sf2 = ScoreFormat(u2['profile']['score_format'])
		sum1 = 0
		sum2 = 0
		smult = 0
		shared1 = []
		shared2 = []
		for i in u1['lists'][kind]:
			e = u1['lists'][kind][i]
			ii = [i]
			if u1['service'] == Service.ANILIST and u2['service'] == Service.MYANIMELIST:
				ii = Resources.al2mal2al.al2mal(kind, i, [])
			if u1['service'] == Service.MYANIMELIST and u2['service'] == Service.ANILIST:
				ii = Resources.al2mal2al.mal2al(kind, i, [])
			for s in ii:
				s = str(s)
				if s != None and s != "None" and s in u2['lists'][kind]:
					s1 = sf1.normalized_score(e['score'])
					s2 = sf2.normalized_score(u2['lists'][kind][s]['score'])
					if not s1 or not s2:
						continue
					# print(f"{u1['profile']['name']} x {u2['profile']['name']} -- {i} : {s} :: {type(s1)}[{s1}] {type(s2)}[{s2}]")
					shared1.append(s1)
					shared2.append(s2)
					sum1 = sum1 + s1
					sum2 = sum2 + s2
					smult += s1 * s2

		num_shared = len(shared1)

		if num_shared == 0:
			return (0,0)
		elif num_shared == 1:
			return (100 - 100/9 * abs(sum1 - sum2))
		
		av1 = sum1/num_shared
		av2 = sum2/num_shared
		sdv1 = statistics.stdev(shared1)
		sdv2 = statistics.stdev(shared2)
		pcc = (smult - num_shared*av1*av2) / ((num_shared - 1)*sdv1*sdv2)

		# diff = 0
		# for i in range(num_shared):
		# 	diff = diff + abs( ((shared1[i] - av1)/sdv1) - ((shared2[i] - av2)/sdv2) )

		return (pcc*100, num_shared)
	except Exception as e:
		print(sys.exc_info())
		traceback.print_exc()
		return (0,0)
