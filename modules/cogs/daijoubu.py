import logging, discord, re
logger = logging.getLogger(__name__)

from discord.ext import commands


class Daijoubu(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def is_daijoubu_server(ctx):
        return ctx.guild.id in [543836696043847690, 561273252354457606, 554770485079179264]

    @commands.Cog.listener()
    async def on_message(self, ctx):
        # # uncomment to limit functionality to specific guilds
        # if not self.is_daijoubu_server(ctx):
        #     return
        
        if ctx.content.lower() == "what" or ctx.content.lower() == ("what?") and ctx.guild.id != 147255790078656513:
            async for i in ctx.channel.history(limit=10):
                l = i.content.lower()
                if l not in ["what", ""] and i.author != ctx.author:
                    s = re.sub("\*+", "", l)
                    msg = "**"+s.upper()+"**"
                    await ctx.channel.send(msg)
                    break
