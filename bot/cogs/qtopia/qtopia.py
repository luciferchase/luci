import discord
from discord.ext import commands


class Qtopia(commands.Cog):
    """Various commands exclusively for Qtopia"""

    def __init__(self, bot):
        self.bot = bot
        self.guild = self.bot.get_guild(587139618999369739)

    @commands.command()
    async def vent1(self, ctx, *message):
        if isinstance(ctx.channel, discord.channel.DMChannel) and message.author in self.guild.members:
            message = " ".join(message)
            channel = self.bot.get_channel(739150769722228806)
            await ctx.send(message)
            await ctx.send(f"{message.author.name} message sent to #vent-1")

    @commands.command()
    async def vent2(self, ctx, *message):
        if isinstance(ctx.channel, discord.channel.DMChannel) and message.author in self.guild.members:
            message = " ".join(message)
            channel = self.bot.get_channel(793407631066005554)
            await ctx.send(message)
            await ctx.send(f"{message.author.name} message sent to #vent-2")

    @commands.command()
    async def ask(self, ctx, *message):
        if isinstance(ctx.channel, discord.channel.DMChannel) and message.author in self.guild.members:
            message = " ".join(message)
            channel = self.bot.get_channel(639902815849938975)
            await ctx.send(message)
            await ctx.send(f"{message.author.name} message sent to #q-and-a")
