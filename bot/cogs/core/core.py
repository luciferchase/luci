import discord
from discord.ext import commands, tasks

import logging

from cogs.meme.meme import Meme


class Core(commands.Cog):
	"""Core commands"""	
	def __init__(self, bot):
		self.bot = bot
		self.log = logging.getLogger("core")

	@commands.Cog.listener()
	async def on_ready(self):
		try:
			await self.bot.change_presence(
				status = discord.Status.idle, 
				activity = discord.Activity(
					type = discord.ActivityType.listening,
					name = "your heartbeats"
					)
				)
			print("Activity set successfully")
		except:
			self.log.warning("Cannot set activity")
		
		print("Connected to discord")

	@commands.Cog.listener()
	async def on_member_join(self, member):
		channel = member.guild.system_channel
			
		if channel is not None:
			embed = discord.Embed(
				title = f"Welcome @{member.name}", 
				description = f"Ayeeeee! Welcome to {member.guild.name} 😁😁"
			) 
			embed.set_thumbnail(url = member.avatar_url) 
			await channel.send(embed = embed)

	@commands.command()
	async def ping(self, ctx) :
		await ctx.send(f"🏓 Pong with {str(round(self.bot.latency, 3))}")


class Scheduler(commands.Cog):
	"""Schedule vairous commands"""

	def __init__(self):
		# Run Schdelued Tasks
		print("Running Scheduled Tasks")
		self.scheduled.start()

	# Scheduled tasks
	@tasks.loop(seconds = 30)
	async def scheduled(self):
		Meme.meme()