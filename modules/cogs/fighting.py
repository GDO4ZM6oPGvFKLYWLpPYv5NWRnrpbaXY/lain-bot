import discord
from discord.ext import commands

from modules.fighting.fginfo import FgInfo
from modules.fighting.fgalias import FgAlias
from modules.core.client import Client

class Fighting(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    async def xiii(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Invalid xiii command passed...')

    @xiii.command(pass_context=True)
    async def fd(self, ctx, char, move):
        channel = ctx.message.channel
        error = 0
        try:
            frames = FgInfo.searchFd("xiii", char, move)

            name = FgAlias.char("xiii", char, "Name")
            nameString = FgAlias.char("xiii", char, "String")
            moveName = FgAlias.move("xiii", nameString, move, "KOF")
        except:
            error+=1
        try:
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
            try:
                moveName = frames["Name"][0]
            except:
                pass

            embed = discord.Embed(
                title = "Frame data for "+moveName+" of "+name
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
        except:
            error+=1
        if error!=0:
            await channel.send("An error has occured! Make sure you're spelling everything correctly!")

    @xiii.command(pass_context=True)
    async def char(self, ctx, char):
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
    async def game(self, ctx):
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
