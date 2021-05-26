import discord
from discord.ext import commands

class Moderation(commands.Cog):
    """Moderation commands for admins"""
    def __init__(self, bot):
        self.bot = bot

    #The below code bans player.
    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def ban(ctx, member : discord.Member, *, reason = None):
        await ctx.guild.ban(member, reason = reason)

    #The below code unbans player.
    @commands.command()
    @commands.has_permissions(administrator = True)
    async def unban(ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'Unbanned {user.mention}')
                return
