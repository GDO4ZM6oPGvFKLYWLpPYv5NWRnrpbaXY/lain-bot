import logging, discord
logger = logging.getLogger(__name__)

from discord.ext import commands


class Daijoubu(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def is_daijoubu_server(ctx):
        return ctx.guild.id in [543836696043847690, 561273252354457606]

    @commands.command()
    @commands.check(is_daijoubu_server)
    async def test(self, ctx):
        await ctx.send('Hello World!')

    @commands.Cog.listener()
    @commands.check(is_daijoubu_server)
    async def on_message(self, ctx):
        if ctx.content.lower() == "what":
            async for i in ctx.channel.history(limit=10):
                if i.content.lower() != "what":
                    msg = "**"+i.content+"**"
                    await ctx.channel.send(msg)
                    break
