"""
Originally: https://github.com/phenom4n4n/phen-cogs/tree/master/connect4 (Thanks mate!)
Heavily altered to fit my needs
"""


import discord
from discord.ext import commands

import asyncio
from collections import Counter
from typing import Union

from bot.utils.predicates import MessagePredicate
from cogs.connect4.core import Connect4Game
from cogs.connect4.menus import get_menu

class Connect4(commands.Cog):
    """
    Play Connect 4!
    """
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
            pred = MessagePredicate.yes_or_no(ctx, user = user)
            await ctx.bot.wait_for("message", check = pred, timeout = 60)
        except asyncio.TimeoutError:
            await ctx.send("Game offer declined, cancelling.")
            return False

        if pred.result:
            return True

        await ctx.send("Game cancelled.")
        return False

    @commands.command(aliases = ["c4"])
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