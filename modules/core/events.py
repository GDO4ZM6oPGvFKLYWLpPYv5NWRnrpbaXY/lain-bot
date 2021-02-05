import discord, json, os, string, re
from os import path

from modules.core.client import Client
from modules.config.config import Config
from modules.config.user import User
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
				Config.cfgUpdate(serverID, "Name", serverName)
			else:
				with open(os.getcwd()+"/config/"+serverID+".json", "x") as server_json:
					json_data = {"Name": serverName}
					json.dump(json_data, server_json)

		if not path.exists(os.getcwd()+"/modules/anime/config/alID.json"):
			with open(os.getcwd()+"/modules/anime/config/alID.json", "x") as al_json:
				json_data = {0: 0}
				json.dump(json_data, al_json)


		for user in bot.users:
			userID = str(user.id)
			userName = str(user.name)
			if path.exists(os.getcwd()+"/user/"+userID+".json"):
				User.userUpdate(userID, "Name", userName)
			else:
				with open(os.getcwd()+"/user/"+userID+".json", "x") as user_json:
					json_data = {"Name": userName}
					json.dump(json_data, user_json)

			# for AL Auto-updates
			alID = User.userRead(str(user.id), "alID")
			if alID!=0 or None:
				with open(os.getcwd()+"/modules/anime/config/alID.json", 'r') as al_json:
					json_data = json.load(al_json)
					json_data[str(user.id)] = alID
				with open(os.getcwd()+"/modules/anime/config/alID.json", 'w') as al_json:
					al_json.write(json.dumps(json_data))

	@bot.event
	async def on_member_join(member):
		if str(member) == 'UWMadisonRecWell#3245':
			for guild in bot.guilds:
				if str(guild.id) == '554770485079179264':
					role = discord.utils.get(guild.roles, name='RecWell')
					await discord.Member.add_roles(member, role)
					break
		if Config.cfgRead(str(member.guild.id), "welcomeOn")==True:
			welcomeMsg = Config.cfgRead(str(member.guild.id), "welcomeMsg")
			welcomeMsgFormatted = welcomeMsg.format(member=member.mention)
			await bot.get_channel(Config.cfgRead(str(member.guild.id), "welcomeChannel")).send(welcomeMsgFormatted)

	def determine_reaction(msg, reactions):
		for reaction in reactions:
			if reaction['type'] == 'exact':
				if msg == reaction['trigger']:
					return reaction['response']
			elif reaction['type'] == 'in':
				clean_msg = msg.translate(str.maketrans('', '', string.punctuation))
				if re.search(f"(^| |\n){reaction['trigger']}($| |\n)", clean_msg):
					return reaction['response']
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