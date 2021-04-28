import discord
from discord.utils import get
from discord.ext import commands

import datetime
import typing

class Forward(commands.Cog):
	"""Forward messages to the bot owner, including pictures (max one per message).
	You can also DM someone as the bot with `luci <user_ID> <message>`."""

	def __init__(self, bot):
		self.bot = bot
	
	async def _send_to(self, embed):
		guild = self.bot.get_guild(await self.config.guild_id())
		if not guild:
			return await self._send_to_owners(embed)
		
		channel = guild.get_channel(await self.config.channel_id())
		if not channel:
			return await self._send_to_owners(embed)
		
		ping_role = guild.get_role(await self.config.ping_role_id())
		ping_user = guild.get_member(await self.config.ping_user_id())
		if not ping_role:
			if not ping_user:
				return await channel.send(embed=embed)
			return await channel.send(content=f"{ping_user.mention}", embed=embed)
		if not ping_role.mentionable:
			await ping_role.edit(mentionable=True)
			await channel.send(content=f"{ping_role.mention}", embed=embed)
			await ping_role.edit(mentionable=False)
		else:
			await channel.send(content=f"{ping_role.mention}", embed=embed)

	async def _send_to_owners(self, embed):
		for owner_id in self.bot.owner_ids:
			await self.bot.get_user(owner_id).send(embed=embed)

	@commands.Cog.listener()
	async def on_message_without_command(self, message):
		if message.guild:
			return
		if message.channel.recipient.id in self.bot.owner_ids:
			return
		if message.author == self.bot.user:
			return
		if not (await self.bot.allowed_by_whitelist_blacklist(message.author)):
			return
		if not message.attachments:
			embed = discord.Embed(
				colour=discord.Colour.red(),
				description=message.content,
				timestamp=message.created_at,
			)
			embed.set_author(name=message.author, icon_url=message.author.avatar_url)
			embed.set_footer(text=f"User ID: {message.author.id}")
			await message.author.send("Message has been delivered.")
		else:
			embed = discord.Embed(
				colour=discord.Colour.red(),
				description=message.content,
				timestamp=message.created_at,
			)
			embed.set_author(name=message.author, icon_url=message.author.avatar_url)
			embed.set_image(url=message.attachments[0].url)
			embed.set_footer(text=f"User ID: {message.author.id}")
			await message.author.send(
				"Message has been delivered. \
				Note that if you've added multiple attachments, I've sent only the first one."
			)
		await self._send_to(embed)

	@commands.command()
	@commands.is_owner()
	async def dm(self, ctx: commands.Context, user_id: int, *, message: str):
		"""DMs a person."""
		destination = get(ctx.bot.get_all_members(), id = user_id)
		await ctx.send(ctx.bot.get_all_members())
		if not destination:
			return await ctx.send("Invalid ID or user not found. You can only send messages to people I share a server with.")
		await destination.send(message)
		await ctx.send(f"Sent message to {destination}.")

	@commands.is_owner()
	@commands.command()
	@commands.guild_only()
	@commands.bot_has_permissions(add_reactions=True)
	async def self(self, ctx: commands.Context, *, message: str):
		"""Send yourself a DM. Owner command only."""
		await ctx.author.send(message)
		await ctx.tick()

	@commands.group(autohelp=True, aliases=["forwarding"])
	@commands.is_owner()
	@commands.guild_only()
	async def forwardset(self, ctx: commands.Context):
		"""Various Forwarding settings."""

	@forwardset.command(name="channel")
	async def forwardset_channel(
		self, ctx: commands.Context, *, channel: typing.Optional[discord.TextChannel]
	):
		"""Set a channel in the current guild to be used for forwarding."""
		if channel:
			await self.config.guild_id.set(ctx.guild.id)
			await self.config.channel_id.set(channel.id)
			await ctx.send(f"I will forward all DMs to {channel.mention}.")
		else:
			await self.config.guild_id.clear()
			await self.config.channel_id.clear()
			await ctx.send("I will forward all DMs to you.")

	@forwardset.command(name="ping")
	async def forwardset_ping(
		self, ctx: commands.Context, *, ping: typing.Union[discord.Role, discord.Member, None]
	):
		"""Set a role or a member to be pinged for forwarding."""
		if ping:
			if isinstance(ping, discord.Role):
				await self.config.ping_role_id.set(ping.id)
			else:
				await self.config.ping_user_id(ping.id)
			await ctx.send(f"I will ping {ping.name}.\n"
			f"Remember to `{ctx.clean_prefix}forwardset channel`")
		else:
			await self.config.ping_role_id.clear()
			await self.config.ping_user_id.clear()
			await ctx.send("I will not ping any role nor member.")

	@forwardset.command(name="settings")
	async def forwardset_settings(self, ctx: commands.Context):
		"""See current settings."""
		data = await self.config.all()

		channel = ctx.guild.get_channel(data["channel_id"])
		channel = "None" if not channel else channel.mention

		role = ctx.guild.get_role(data["ping_role_id"])
		role = "None" if not role else role.name

		user = ctx.guild.get_member(data["ping_user_id"])
		user = "None" if not user else user.name

		embed = discord.Embed(
			colour=await ctx.embed_colour(), timestamp=datetime.datetime.now()
		)
		embed.set_author(name=ctx.guild.name, icon_url=ctx.guild.icon_url)
		embed.title = "**__Unique Name settings:__**"
		embed.set_footer(text="*required to function properly")

		embed.add_field(name="Forwarding to channel:", value=channel)
		embed.add_field(name="Pinged role:", value=role)
		embed.add_field(name="Pinged member:", value=user)

		await ctx.send(embed=embed)
