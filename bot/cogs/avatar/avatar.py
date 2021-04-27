# Discord
import discord
from discord.ext import commands

class Avatar(commands.Cog):
    """Get user's avatar URL."""

    @commands.command(aliases = ["av"])
    async def avatar(self, ctx, *, user: discord.Member = None):
        """Returns user avatar URL.

        User argument can be user mention, nickname, username, user ID.
        Default to yourself when no argument is supplied.
        """
        author = ctx.author

        if not user:
            user = author

        if user.is_avatar_animated():
            url = user.avatar_url_as(format = "gif")
        if not user.is_avatar_animated():
            url = user.avatar_url_as(static_format = "png")

        await ctx.send("{}'s Avatar URL : {}".format(user.name, url))
