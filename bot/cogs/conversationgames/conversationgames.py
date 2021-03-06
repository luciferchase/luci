import discord
from discord.ext import commands

import random

from cogs.conversationgames.dares import dares
from cogs.conversationgames.nhie import nhie
from cogs.conversationgames.topic import topic
from cogs.conversationgames.truths import truths
from cogs.conversationgames.wyr import wyr


class ConversationGames(commands.Cog):
    """Conversation Games"""

    def __init__(self):
        self.dares = dares
        self.nhie = nhie
        self.topic = topic
        self.truths = truths
        self.wyr = wyr
        
    @commands.command(aliases = ["aliven"])
    @commands.bot_has_permissions(embed_links = True)
    async def topic(self, ctx):
        """Start the conversation"""

        embed = discord.Embed(
            title = "Topic",
            description = random.choice(self.topic),
            color = 0xf34949                                # Red
        )
        await ctx.send(embed = embed)
    
    @commands.command(aliases = ["wyr"])
    @commands.bot_has_permissions(embed_links = True)
    async def wouldyourather(self, ctx):
        """Would you rather?"""

        embed = discord.Embed(
            title = "Would you rather..",
            description = random.choice(self.wyr),
            color = 0xf34949                                # Red
        )
        await ctx.send(embed = embed)

    @commands.command(aliases = ["nhie"])
    @commands.bot_has_permissions(embed_links = True)
    async def neverhaveiever(self, ctx):
        """Never have I ever"""

        embed = discord.Embed(
            title = "Never have I ever...",
            description = random.choice(self.nhie),
            color = 0xf34949                                # Red
        )
        await ctx.send(embed = embed)

    @commands.command()
    @commands.bot_has_permissions(embed_links = True)
    async def truth(self, ctx, *, user: discord.Member):
        """Ask a truth question to users!"""
        
        question = random.choice(self.truths)

        # Set author
        author = ctx.message.author

        # Get and pick random user
        member_list = len(ctx.guild.members)
        random_number = random.randint(0, member_list - 1)
        random_member = ctx.guild.members[random_number].mention

        # Build Embed
        embed = discord.Embed(
            title = f"{author.nick} asked {user.nick}",
            description = question.format(name = random_member),
            color = 0xf34949                            # red
        )
        await ctx.send(embed = embed)

    @commands.command()
    @commands.bot_has_permissions(embed_links = True)
    async def dare(self, ctx, *, user: discord.Member):
        """Dare someone!"""

        question = random.choice(self.dares)

        # Set author
        author = ctx.message.author

        # Get and pick random user
        member_list = len(ctx.guild.members)
        random_number = random.randint(0, member_list - 1)
        random_member = ctx.guild.members[random_number].mention

        # Build Embed
        embed = discord.Embed(
            title = f"{author.nick} dared {user.nick}",
            description = question.format(name = random_member),
            color = 0xf34949                    # Red
        )                           
        await ctx.send(embed = embed)
