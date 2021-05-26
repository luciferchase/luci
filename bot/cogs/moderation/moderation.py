import discord
from discord.ext import commands

class Moderation(commands.Cog):
    """Moderation commands for admins"""
    def __init__(self, bot):
        self.bot = bot

    async def ban(self, member, *reason):
        await member.ban()