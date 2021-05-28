import discord
from discord.ext import commands


class Qtopia(commands.Cog):
    """Various commands exclusively for Qtopia"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        # If the message is from the bot itself then return
        if (message.author == self.bot.user):
            return

        if (message.guild is None and not message.author.bot and message.author != luci):
            # Vent channels
            if (message.content.startswith.lower() == "luci vent1"):
                send_message = message[9:]
                channel = self.bot.get_channel(739150769722228806)
                await ctx.send(message)
                await ctx.send(f"{message.author.name} message sent to #vent-1")

            if (message.content.startswith.lower() == "luci vent2"):
                send_message = message[9:]
                channel = self.bot.get_channel(793407631066005554)
                await ctx.send(message)
                await ctx.send(f"{message.author.name} message sent to #vent-2")

            # q-and-a channels
            if (message.content.startswith.lower() == "luci ask"):
                send_message = message[7:]
                channel = self.bot.get_channel(639902815849938975)
                await ctx.send(message)
                await ctx.send(f"{message.author.name} message sent to #q-and-a")