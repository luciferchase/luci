import discord
from discord.ext import commands

import asyncio

from bot.utils.converters import GetFetchUser


class Mod(commands.Cog):
    """Moderation commands for admins"""

    def __init__(self, bot):
        self.bot = bot
        self.GetFetchUser = GetFetchUser()

    async def format_mod_embed(self, ctx, user, success, method, duration = None, location = None):
        """Helper function to format an embed to prevent extra code"""
        
        embed = discord.Embed(timestamp = ctx.message.created_at)
        embed.set_author(name = method.title(), icon_url = user.avatar_url)
        embed.color = 0xf34949
        embed.set_footer(text = f"User ID: {user.id}")
        
        if success:
            if method == "ban" or method == "hackban":
                embed.description = f"{user} was just {method}ned."
            elif method == "unmute":
                embed.description = f"{user} was just {method}d."
            elif method == "mute":
                embed.description = f"{user} was just {method}d for {duration}."
            elif method == "channel-locked" or method == "server-locked":
                embed.description = f"`{location.name}` is now in lockdown mode!"
            elif method == "channel-unlocked" or method == "server-unlocked":
                embed.description = f"`{location.name}` is now unlocked. Enjoy!"
            else:
                embed.description = f"{user} was just {method}ed."
        else:
            if method == "lock" or "channel-locked":
                embed.description = f"You do not have the permissions to {method} `{location.name}`."
            if method == "unlock" or "channel-unlocked":
                embed.description = f"You do not have the permissions to {method} `{location.name}`."
            else:
                embed.description = f"You do not have the permissions to {method} {user.name}."
        
        return embed

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def kick(self, ctx, member: discord.Member, *, reason = None):
        """Kick someone from the server."""

        try:
            await ctx.guild.kick(member, reason = reason)
        except:
            success = False
        else:
            success = True

        embed = await self.format_mod_embed(ctx, member, success, "kick")
        await ctx.send(embed = embed)

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def ban(self, ctx, member: discord.Member, *, reason = None):
        """Ban someone from the server."""

        if (member == ctx.author):
            await ctx.send("Boomer! you can't ban yourself 🤦‍♂️")

        try:
            await ctx.guild.ban(member, reason = reason)
            await member.send(f"You have been banned in {ctx.guild} for {reason}" if reason != None \
                else f"You have been banned in {ctx.guild}")
        except:
            success = False
        else:
            success = True

        embed = await self.format_mod_embed(ctx, member, success, "ban")
        await ctx.send(embed = embed)

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def unban(self, ctx, member: GetFetchUser, *, reason = None):
        """Unban a User"""

        try:
            await ctx.guild.unban(user = member, reason = reason)
        except:
            success = False
        else:
            await member.send(f"You have been unbanned in {ctx.guild} for {reason}" if reason != None \
                else f"You have been unbanned in {ctx.guild}")
            success = True

        embed = await self.format_mod_embed(ctx, member, success, "unban")
        await ctx.send(embed = embed)

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def purge(self, ctx, limit : int, member: discord.Member = None):
        """Clean a number of messages"""

        if member is None:
            await ctx.purge(limit = limit + 1)
        else:
            async for message in ctx.channel.history(limit = limit + 1):
                if message.author is member:
                    await message.delete()

    @commands.command()
    async def clean(self, ctx, quantity: int):
        """ Clean a number of your own messages
        Usage: luci clean 5 """

        if quantity <= 15:
            total = quantity + 1
            async for message in ctx.channel.history(limit = total):
                if message.author == ctx.author:
                    await message.delete()
                    await asyncio.sleep(3.0)
        else:
            async for message in ctx.channel.history(limit = 6):
                if message.author == ctx.author:
                    await message.delete()
                    await asyncio.sleep(3.0)

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def bans(self, ctx):
        """See a list of banned users in the guild"""

        bans = await ctx.guild.bans()
    
        embed = discord.Embed(title = f"List of Banned Members ({len(bans)}):")
        embed.description = ", ".join([str(b.user) for b in bans])
        embed.color = 0xf34949

        await ctx.send(embed = embed)

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def baninfo(self, ctx, *, member: GetFetchUser):
        """Check the reason of a ban from the audit logs."""

        ban = await ctx.guild.fetch_ban(member)

        embed = discord.Embed()
        embed.color = 0xf34949
        embed.set_author(name = str(ban.user), icon_url = ban.user.avatar_url)
        embed.add_field(name="Reason", value = ban.reason or "None")
        embed.set_thumbnail(url = ban.user.avatar_url)
        embed.set_footer(text = f"User ID: {ban.user.id}")

        await ctx.send(embed = embed)

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def addrole(self, ctx, member: discord.Member, *, rolename: str):
        """Add a role to someone else."""

        role = discord.utils.find(lambda m: rolename.lower() in m.name.lower(), ctx.message.guild.roles)

        if not role:
            return await ctx.send("That role does not exist.")
        try:
            await member.add_roles(role)
            await ctx.send(f"Added: `{role.name}`")
        except:
            await ctx.send("I don't have the perms to add that role.")


    @commands.command()
    @commands.has_permissions(administrator = True)
    async def removerole(self, ctx, member: discord.Member, *, rolename: str):
        """Remove a role from someone else."""

        role = discord.utils.find(lambda m: rolename.lower() in m.name.lower(), ctx.message.guild.roles)
        if not role:
            return await ctx.send("That role does not exist.")
        try:
            await member.remove_roles(role)
            await ctx.send(f"Removed: `{role.name}`")
        except:
            await ctx.send("I don't have the perms to add that role.")

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def hackban(self, ctx, userid, *, reason = None):
        """Ban someone not in the server"""

        try:
            userid = int(userid)
        except:
            await ctx.send("Invalid ID!")
        
        try:
            await ctx.guild.ban(discord.Object(userid), reason = reason)
        except:
            success = False
        else:
            success = True

        if success:
            async for entry in ctx.guild.audit_logs(limit = 1, user = ctx.guild.me, 
                action = discord.AuditLogAction.ban):
                embed = await self.format_mod_embed(ctx, entry.target, success, "hackban")
        else:
            embed = await self.format_mod_embed(ctx, userid, success, "hackban")
        await ctx.send(embed = embed)

    @commands.command()
    @commands.has_permissions(administrator = True)
    async def mute(self, ctx, member: discord.Member, duration, *, reason = None):
        """Denies someone from chatting in all text channels and \
        talking in voice channels for a specified duration
        Example: luci mute @luciferchase 1h"""

        unit = duration[-1]
        
        if unit == "s":
            time = int(duration[:-1])
            longunit = "seconds"
        elif unit == "m":
            time = int(duration[:-1]) * 60
            longunit = "minutes"
        elif unit == "h":
            time = int(duration[:-1]) * 60 * 60
            longunit = "hours"
        else:
            await ctx.send("Invalid Unit! Use `s`, `m`, or `h`.")
            return

        progress = await ctx.send("Muting user!")
        
        try:
            for channel in ctx.guild.text_channels:
                await channel.set_permissions(
                    member, 
                    overwrite = discord.PermissionOverwrite(send_messages = False), 
                    reason = reason
                )

            for channel in ctx.guild.voice_channels:
                await channel.set_permissions(
                    member, 
                    overwrite = discord.PermissionOverwrite(speak = False), 
                    reason = reason
                )
        except:
            success = False
        else:
            success = True
            
        await progress.delete()

        embed = await self.format_mod_embed(ctx, member, success, "mute", f"{str(duration[:-1])} {longunit}")
        await ctx.send(embed = embed)
        
        await asyncio.sleep(time)
        
        try:
            for channel in ctx.guild.channels:
                await channel.set_permissions(member, overwrite = None, reason = reason)
        except:
            pass
        
    @commands.command()
    async def unmute(self, ctx, member: discord.Member, *, reason = None):
        """Removes channel overrides for specified member"""

        progress = await ctx.send("Unmuting user!")
        
        try:
            for channel in ctx.message.guild.channels:
                await channel.set_permissions(member, overwrite = None, reason = reason)
        except:
            success = False
        else:
            success = True

        await progress.delete()
            
        embed = await self.format_mod_embed(ctx, member, success, "unmute")
        await ctx.send(embed = embed)

    @commands.group(invoke_without_command = True)
    @commands.has_permissions(administrator = True)
    async def lock(self, ctx):
        """Server/Channel lock"""
        pass

    @lock.command(aliases=["channel"])
    async def chan(self, ctx, channel: discord.TextChannel = None, *, reason = None):
        """Lockdown a channel. Members will not be able to send a message."""

        if channel is None: 
            channel = ctx.channel
        
        try:
            await channel.set_permissions(
                ctx.guild.default_role, 
                overwrite = discord.PermissionOverwrite(send_messages = False), 
                reason = reason
            )
        except:
            success = False
        else:
            success = True
        
        embed = await self.format_mod_embed(ctx, ctx.author, success, "channel-locked", 0, channel)
        await ctx.send(embed = embed)
    
    @lock.command(name = "server")
    async def _server(self, ctx, server: discord.Guild = None, *, reason = None):
        """Lockdown the server. Sed lyf."""

        if server is None: 
            server = ctx.guild
        
        progress = await ctx.send(f"Locking down {server.name}")
        
        try:
            for channel in server.channels:
                await channel.set_permissions(
                    ctx.guild.default_role, 
                    overwrite = discord.PermissionOverwrite(send_messages = False), 
                    reason = reason
                )
        except:
            success = False
        else:
            success = True
        
        await progress.delete()
        
        embed = await self.format_mod_embed(ctx, ctx.author, success, "server-locked", 0, server)
        await ctx.send(embed = embed)

    @commands.group(invoke_without_command = True)
    @commands.has_permissions(administrator = True)
    async def unlock(self, ctx):
        """Server/Channel unlock"""
        pass

    @unlock.command(aliases=["chan"])
    async def channel(self, ctx, channel: discord.TextChannel = None, *, reason = None):
        """Unlock a channel. Members will be able to send message again."""

        if channel is None: 
            channel = ctx.channel
        
        try:
            await channel.set_permissions(
                ctx.guild.default_role, 
                overwrite = discord.PermissionOverwrite(send_messages = True), 
                reason = reason
            )
        except:
            success = False
        else:
            success = True
        
        embed = await self.format_mod_embed(ctx, ctx.author, success, "channel-unlocked", 0, channel)
        await ctx.send(embed = embed)
    
    @unlock.command()
    async def server(self, ctx, server: discord.Guild = None, *, reason = None):
        """Unlock the server. Sed lyf."""
        
        if server is None: 
            server = ctx.guild
        
        progress = await ctx.send(f"Unlocking {server.name}")
        
        try:
            for channel in server.channels:
                await channel.set_permissions(
                    ctx.guild.default_role, 
                    overwrite = discord.PermissionOverwrite(send_messages = True), 
                    reason = reason
                )
        except:
            success = False
        else:
            success = True
        
        await progress.delete()
        
        embed = await self.format_mod_embed(ctx, ctx.author, success, "server-unlocked", 0, server)
        await ctx.send(embed = embed)