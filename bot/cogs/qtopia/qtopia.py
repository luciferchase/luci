import discord
from discord.ext import commands


class Qtopia(commands.Cog):
    """Various commands exclusively for Qtopia"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def vent1(self, ctx, *message):
        """Send anonymous question to #vent-1. DM only Command."""
        if isinstance(ctx.channel, discord.channel.DMChannel):
            message = " ".join(message)
            channel = await self.bot.fetch_channel(739150769722228806)
            await ctx.send(message)
            await ctx.send(f"{ctx.author.name} message sent to #vent-1")

    @commands.command()
    async def vent2(self, ctx, *message):
        """Send anonymous question to #vent-2. DM only Command."""
        if isinstance(ctx.channel, discord.channel.DMChannel):
            message = " ".join(message)
            channel = await self.bot.fetch_channel(793407631066005554)
            await ctx.send(message)
            await ctx.send(f"{ctx.author.name} message sent to #vent-2")

    @commands.command()
    async def ask(self, ctx, *message):
        """Send anonymous question to #q-and-a. DM only Command."""
        if isinstance(ctx.channel, discord.channel.DMChannel):
            message = " ".join(message)
            channel = await self.bot.fetch_channel(639902815849938975)
            await ctx.send(message)
            await ctx.send(f"{ctx.author.name} message sent to #q-and-a")
