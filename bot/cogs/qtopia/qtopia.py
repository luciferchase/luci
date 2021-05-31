import discord
from discord.ext import commands

import json


class Qtopia(commands.Cog):
    """Various commands exclusively for Qtopia"""

    def __init__(self, bot):
        self.bot = bot
        self.server_id = 587139618999369739

    @commands.command()
    async def vent1(self, ctx, *message):
        """Send anonymous question to #vent-1. DM only Command."""
        
        if isinstance(ctx.channel, discord.channel.DMChannel):
            message = " ".join(message)
            channel = await self.bot.fetch_channel(739150769722228806)
            
            await channel.send(f"[Anonymous message]\n{message}")
            confirmation_message = await ctx.send(f"{ctx.author.name} message sent to #vent-1")

            with open("/app/bot/cogs/qtopia/logs.json", "r+") as logs:
                data = json.load(logs)

                if (len(data["vent1"]) == 10):
                    data.pop()

                data["vent1"].insert(0, [ctx.author.id, message[:50], 
                    confirmation_message.created_at.strftime("%d-%m-%Y | %H:%M")])

            with open("/app/bot/cogs/qtopia/logs.json", "w") as logs:
                json.dump(data, logs)

    @commands.command()
    async def vent2(self, ctx, *message):
        """Send anonymous question to #vent-2. DM only Command."""
        
        if isinstance(ctx.channel, discord.channel.DMChannel):
            message = " ".join(message)
            channel = await self.bot.fetch_channel(793407631066005554)
            
            await channel.send(f"[Anonymous Message]\n{message}")
            confirmation_message = await ctx.send(f"{ctx.author.name} message sent to #vent-2")

            with open("/app/bot/cogs/qtopia/logs.json", "r+") as logs:
                data = json.load(logs)

                if (len(data["vent2"]) == 10):
                    data.pop()

                data["vent2"].insert(0, [ctx.author.id, message[:50], 
                    confirmation_message.created_at.strftime("%d-%m-%Y | %H:%M")])

            with open("/app/bot/cogs/qtopia/logs.json", "w") as logs:
                json.dump(data, logs)

    @commands.command()
    async def ask(self, ctx, *message):
        """Send anonymous question to #q-and-a. DM only Command."""
        
        if isinstance(ctx.channel, discord.channel.DMChannel):
            message = " ".join(message)
            channel = await self.bot.fetch_channel(639902815849938975)
            
            await channel.send(f"[Anonymous Message]\n{message}")
            confirmation_message = await ctx.send(f"{ctx.author.name} message sent to #q-and-a")

            with open("/app/bot/cogs/qtopia/logs.json", "r+") as logs:
                data = json.load(logs)

                if (len(data["ask"]) == 10):
                    data.pop()

                data["ask"].insert(0, [ctx.author.id, message[:50], 
                    confirmation_message.created_at.strftime("%d-%m-%Y | %H:%M")])

            with open("/app/bot/cogs/qtopia/logs.json", "w") as logs:
                json.dump(data, logs)

    @commands.command()
    @commands.has_permissions(ban_members = True)
    async def log(self, ctx, channel, number = 1):
        """See details of upto last 10 annon messages. Please don't abuse."""

        with open("/app/bot/cogs/qtopia/logs.json", "r") as logs:
            data = json.load(logs)

            if (len(data[channel]) == 0):
                await ctx.send(f"No recent message sent to {channel}")

            message_string = ""
            for i in range(number):
                temp_data = data[channel][i]
                member = await self.bot.fetch_user(temp_data[0])

                message_string += "{}. Author: {}\nAuthor-id: {}\nMessage: {}...\nTime: {}\n".format(i + 1, 
                    f"{member.name}#{member.discriminator}", member.id, temp_data[1], temp_data[2]) 

            await ctx.send("```css\n{}```".format(message_string))

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    async def unverified(self, ctx):
        """Give unverified role to all those who doesn't have any role"""
        guild = await self.bot.fetch_guild(587139618999369739)

        count = 0
        message_string = ""
        async for member in guild.fetch_members():
            roles = [role.name.lower() for role in member.roles]
            if ("qtopians" in roles or "bots" in roles or "unverified" in roles):
                pass
            else:
                role = discord.utils.find(lambda m: "unverified" in m.name.lower(), guild.roles)
                await member.add_roles(role)
                count += 1
                message_string += str(member.id) + "\n"

        await ctx.send(f"{count} were given the @Unverified role. Here are the IDs.")
        try:
            await ctx.send("```css\n{}```".format(message_string))
        except:
            print(message_string)
            await ctx.send("Message too long to send here. IDs are printed to console.")

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
    async def norole(self, ctx):
        """Check members who don't have any roles"""
        guild = await self.bot.fetch_guild(587139618999369739)

        count = 0
        message_string = ""
        async for member in guild.fetch_members():
            roles = [role.name.lower() for role in member.roles]
            if ("qtopians" in roles or "bots" in roles or "unverified" in roles):
                pass
            else:
                message_string += str(member.id) + "\n"

        await ctx.send(f"{count} members don't have any role to them. Here are the IDs.")
        try:
            await ctx.send("```css\n{}```".format(message_string))
        except:
            print(message_string)
            await ctx.send("Message too long to send here. IDs are printed to console.")

    # Check-in
    @commands.Cog.listener()
    async def on_message(self, message):
        if (message.channel.id == 845817544484323349):
            reactions = ["❤", "🧡", "💛", "🤍", "🖤", "💚", "💙", "💜", "💔"]

            for reaction in reactions:
                await message.add_reaction(reaction)
