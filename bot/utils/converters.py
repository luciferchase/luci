import discord
from discord import User
from discord.ext.commands import BadArgument, Context, Converter, MemberConverter, UserConverter

class GetFetchUser(UserConverter):
    async def convert(self, ctx, user: str) -> User:
        """
        :param user: str argument coming from Discord.
        Tries to get user from cache and if fails tries to fetch user from Discord.
        If both fail raises BadArgument
        """
        try:
            return await super().convert(ctx, user)
        except BadArgument:
            try:
                user_id = int(user)
            except ValueError:
                raise BadArgument("Can't convert to neither user nor snowflake.")
            else:
                try:
                    return await ctx.bot.fetch_user(user_id)
                except HTTPException as e:
                    raise BadArgument(e)
