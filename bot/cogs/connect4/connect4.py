"""
Originally: https://github.com/phenom4n4n/phen-cogs/tree/master/connect4 (Thanks mate!)
Heavily altered to fit my needs
"""


import discord
from discord.ext import commands

import asyncio
from babel.numbers import format_decimal
from collections import Counter
from typing import Union

from cogs.connect4.core import Connect4Game
from cogs.connect4.menus import get_menu
from cogs.connect4.predicates import MessagePredicate


def humanize_number(val: Union[int, float]) -> str:
    """
    Convert an int or float to a str with digit separators based on bot locale

    Parameters
    ----------
    val : Union[int, float]
        The int/float to be formatted.
    override_locale: Optional[str]
        A value to override bot's regional format.

    Returns
    -------
    str
        locale aware formatted number.
    """
    return format_decimal(val)

class Connect4(commands.Cog):
    """
    Play Connect 4!
    """

    EMOJI_MEDALS = {
        1: "\N{FIRST PLACE MEDAL}",
        2: "\N{SECOND PLACE MEDAL}",
        3: "\N{THIRD PLACE MEDAL}",
    }

    def __init__(self, bot):
        self.bot = bot
        defaults = {
            "stats": {
                "played": 0, 
                "ties": 0, 
                "wins": {}, 
                "losses": {}, 
                "draws": {}
            }
        }

    @staticmethod
    async def startgame(ctx: commands.Context, user: discord.Member) -> bool:
        """
        Whether to start the connect 4 game.
        """
        await ctx.send(
            f"{user.mention}, {ctx.author.name} is challenging you to a game of Connect4. (y/n)"
        )

        try:
            pred = MessagePredicate.yes_or_no(ctx, user=user)
            await ctx.bot.wait_for("message", check=pred, timeout=60)
        except asyncio.TimeoutError:
            await ctx.send("Game offer declined, cancelling.")
            return False

        if pred.result:
            return True

        await ctx.send("Game cancelled.")
        return False

    @commands.command()
    async def connect4(self, ctx: commands.Context, member: discord.Member):
        """
        Play Connect 4 with another player.
        """
        if member.bot:
            return await ctx.send("That's a bot, silly!")
        if ctx.author == member:
            return await ctx.send("You can't play yourself!")
        if not await self.startgame(ctx, member):
            return

        game = Connect4Game(ctx.author, member)
        menu = get_menu()(self, game)
        await menu.start(ctx)

    def create_field(self, stats: dict, key: str) -> dict:
        counter = Counter(stats[key])
        values = []
        total = sum(counter.values())
        for place, (user_id, win_count) in enumerate(counter.most_common(3), 1):
            medal = self.EMOJI_MEDALS[place]
            values.append(f"{medal} <@!{user_id}>: {win_count}")
        return (
            {"name": f"{key.title()}: {total}", "value": "\n".join(values), "inline": True}
            if values
            else {}
        )