import discord, json, os, string, re, random
from os import path

from modules.core.client import Client
from modules.core.resources import Resources

bot = Client.bot

status = discord.Game("on Wired") #sets the game the bot is currently playing
esportsStatus = discord.Game("King of Fighters XIII")

class Events:

	@bot.event
	async def on_ready(): #bot startup event

		if bot.user.id == 727537208235524178:
			print('Esports Club is ready to go!')
			bot.command_prefix = ">"
			await bot.change_presence(status=discord.Status.online, activity=esportsStatus)
		else:
			print('Lain is online!')
			await bot.change_presence(status=discord.Status.online, activity=status)

		for guild in bot.guilds:
			serverID = str(guild.id)
			serverName = str(guild.name)
			if path.exists(os.getcwd()+"/config/"+serverID+".json"):
				Resources.config.cfgUpdate(serverID, "Name", serverName)
			else:
				with open(os.getcwd()+"/config/"+serverID+".json", "x") as server_json:
					json_data = {"Name": serverName}
					json.dump(json_data, server_json)


	@bot.event
	async def on_member_join(member):
		if str(member) == 'UWMadisonRecWell#3245':
			for guild in bot.guilds:
				if str(guild.id) == '554770485079179264':
					role = discord.utils.get(guild.roles, name='RecWell')
					await discord.Member.add_roles(member, role)
					break
		if Resources.config.cfgRead(str(member.guild.id), "welcomeOn")==True:
			welcomeMsg = Resources.config.cfgRead(str(member.guild.id), "welcomeMsg")
			welcomeMsgFormatted = welcomeMsg.format(member=member.mention)
			await bot.get_channel(Resources.config.cfgRead(str(member.guild.id), "welcomeChannel")).send(welcomeMsgFormatted)

	def determine_reaction(msg, reactions):
		for reaction in reactions:
			if reaction['type'] == 'exact':
				if msg == reaction['trigger']:
					if 'response' in reaction:
						return reaction['response']
					else:
						return reaction['responses'][random.randint(0, len(reaction['responses'])-1)]
			elif reaction['type'] == 'in':
				clean_msg = msg.translate(str.maketrans('', '', string.punctuation))
				if re.search(f"(^| |\n){reaction['trigger']}($| |\n)", clean_msg):
					if 'response' in reaction:
						return reaction['response']
					else:
						return reaction['responses'][random.randint(0, len(reaction['responses'])-1)]
		return None

	@bot.event
	async def on_message(msg):
		try:
			if not msg.author.bot:
				# hard coded will have fastest response time and are global
				if msg.content in ['good bot', 'good bot!', 'good lain']:
					await msg.channel.send('https://files.catbox.moe/jkhrji.png')

				if msg.content in ['bad bot', 'bad bot!', 'bad lain']:
					await msg.channel.send('https://files.catbox.moe/bde830.gif')

				# slower response but on the fly changes and per guild
				reactions = await Resources.guild_col.find_one({'guild_id': str(msg.guild.id), 'reactions': {'$exists': True}}, {'reactions': 1})
				if reactions:
					try:
						reaction = await bot.loop.run_in_executor(None, Events.determine_reaction, msg.content, reactions['reactions'])
						if reaction:
							await msg.channel.send(reaction)
					except:
						pass
		except:
			pass

		await bot.process_commands(msg)