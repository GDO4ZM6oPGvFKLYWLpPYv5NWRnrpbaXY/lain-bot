import discord
from discord.ext import commands

from .client import Client
from .config import Config

bot = Client.bot
game = discord.Game("with her phone") #sets the game the bot is currently playing

class Events:
	
	@bot.event
	async def on_ready(): #bot startup event
		print('Kotori-san is ready to go!')
		await bot.change_presence(status=discord.Status.online, activity=game)
		
		channel = bot.get_channel(Config._botChannel)
		
		embed = discord.Embed(
			title = 'こんにちは、プロデューサーさん！',
			description = 'Kotori is now online!',
			color = discord.Color.green()
		)
		
		embed.set_image(url='https://cdn.animenewsnetwork.com/thumbnails/fit450x450/cms/news/115267/idol.jpg')
			
		await channel.send(embed=embed)