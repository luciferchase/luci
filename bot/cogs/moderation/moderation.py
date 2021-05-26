import discord
from discord.ext import commands

class Moderation(commands.Cog):
    """Moderation commands for admins"""
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(admin = True)
    async def ban(self, member, *reason):
        """Ban a member [Reason must be given]"""
        await member.ban()