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
            elif method == "unmute" or method == "kick":
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
    @commands.guild_only
    @commands.has_permissions(kick_members = True)
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
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
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
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
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
    @commands.guild_only()
    @commands.has_permissions(view_audit_log = True)
    async def bans(self, ctx):
        """See a list of banned users in the guild"""

        bans = await ctx.guild.bans()
    
        embed = discord.Embed(title = f"List of Banned Members ({len(bans)}):")
        embed.description = ", ".join([str(b.user) for b in bans])
        embed.color = 0xf34949

        await ctx.send(embed = embed)

    @commands.command()
    @commands.guild_only()
    @commands.has_permissions(view_audit_log = True)
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
    @commands.guild_only()
    @commands.has_permissions(manage_roles = True)
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
    @commands.guild_only()
    @commands.has_permissions(manage_roles = True)
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
    @commands.guild_only()
    @commands.has_permissions(ban_members = True)
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
    @commands.guild_only()
    @commands.has_permissions(manage_channel = True)
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
    
    @commands.guild_only()
    @commands.has_permissions(manage_channel = True)
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

    @commands.guild_only()
    @commands.group(invoke_without_command = True)
    @commands.has_permissions(manage_server = True)
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

    @commands.guild_only()
    @commands.group(invoke_without_command = True)
    @commands.has_permissions(manage_server = True)
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

    @commands.command(aliases=["nick"])
    @commands.guild_only()
    @permissions.has_permissions(manage_nicknames = True)
    async def nickname(self, ctx, member: discord.Member, *, name: str = None):
        """Change nickname of a member"""
        try:
            await member.edit(nick = name)
            
            message = f"Changed **{member.name}'s** nickname to **{name}**"
            
            if name is None:
                message = f"Reset **{member.name}'s** nickname"
            await ctx.send(message)
        
        except Exception as e:
            await ctx.send(e)

    @commands.group()
    @commands.guild_only()
    @commands.max_concurrency(1, per=commands.BucketType.guild)
    @permissions.has_permissions(manage_messages=True)
    async def prune(self, ctx):
        """ Removes messages from the current server. """
        if ctx.invoked_subcommand is None:
            await ctx.send_help(str(ctx.command))

    async def do_removal(self, ctx, limit, predicate, *, before=None, after=None, message=True):
        if limit > 2000:
            return await ctx.send(f"Too many messages to search given ({limit}/2000)")

        if not before:
            before = ctx.message
        else:
            before = discord.Object(id=before)

        if after:
            after = discord.Object(id=after)

        try:
            deleted = await ctx.channel.purge(limit=limit, before=before, after=after, check=predicate)
        except discord.Forbidden:
            return await ctx.send("I do not have permissions to delete messages.")
        except discord.HTTPException as e:
            return await ctx.send(f"Error: {e} (try a smaller search?)")

        deleted = len(deleted)
        if message is True:
            await ctx.send(f"🚮 Successfully removed {deleted} message{'' if deleted == 1 else 's'}.")

    @prune.command()
    async def embeds(self, ctx, search=100):
        """Removes messages that have embeds in them."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds))

    @prune.command()
    async def files(self, ctx, search=100):
        """Removes messages that have attachments in them."""
        await self.do_removal(ctx, search, lambda e: len(e.attachments))

    @prune.command()
    async def mentions(self, ctx, search=100):
        """Removes messages that have mentions in them."""
        await self.do_removal(ctx, search, lambda e: len(e.mentions) or len(e.role_mentions))

    @prune.command()
    async def images(self, ctx, search=100):
        """Removes messages that have embeds or attachments."""
        await self.do_removal(ctx, search, lambda e: len(e.embeds) or len(e.attachments))

    @prune.command(name="all")
    async def _remove_all(self, ctx, search=100):
        """Removes all messages."""
        await self.do_removal(ctx, search, lambda e: True)

    @prune.command()
    async def user(self, ctx, member: discord.Member, search=100):
        """Removes all messages by the member."""
        await self.do_removal(ctx, search, lambda e: e.author == member)

    @prune.command()
    async def contains(self, ctx, *, substr: str):
        """Removes all messages containing a substring.
        The substring must be at least 3 characters long.
        """
        if len(substr) < 3:
            await ctx.send("The substring length must be at least 3 characters.")
        else:
            await self.do_removal(ctx, 100, lambda e: substr in e.content)

    @prune.command(name="bots")
    async def _bots(self, ctx, search=100, prefix=None):
        """Removes a bot user's messages and messages with their optional prefix."""

        getprefix = prefix if prefix else self.config["prefix"]

        def predicate(m):
            return (m.webhook_id is None and m.author.bot) or m.content.startswith(tuple(getprefix))

        await self.do_removal(ctx, search, predicate)

    @prune.command(name="users")
    async def _users(self, ctx, prefix=None, search=100):
        """Removes only user messages. """

        def predicate(m):
            return m.author.bot is False

        await self.do_removal(ctx, search, predicate)

    @prune.command(name="emojis")
    async def _emojis(self, ctx, search=100):
        """Removes all messages containing custom emoji."""
        custom_emoji = re.compile(r"<a?:(.*?):(\d{17,21})>|[\u263a-\U0001f645]")

        def predicate(m):
            return custom_emoji.search(m.content)

        await self.do_removal(ctx, search, predicate)

    @prune.command(name="reactions")
    async def _reactions(self, ctx, search=100):
        """Removes all reactions from messages that have them."""

        if search > 2000:
            return await ctx.send(f"Too many messages to search for ({search}/2000)")

        total_reactions = 0
        async for message in ctx.history(limit=search, before=ctx.message):
            if len(message.reactions):
                total_reactions += sum(r.count for r in message.reactions)
                await message.clear_reactions()

        await ctx.send(f"Successfully removed {total_reactions} reactions.")