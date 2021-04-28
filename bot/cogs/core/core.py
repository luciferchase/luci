import discord
from discord.ext import commands, tasks

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import logging

from cogs.meme.meme import Meme

class Core(commands.Cog):
	"""Core commands"""	
	def __init__(self, bot):
		self.bot = bot
		self.log = logging.getLogger("core")

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

		# Initialize scheduler
		scheduler = AsyncIOScheduler()

		# Add jobs to scheduler
		scheduler.add_job(Meme.meme(), CronTrigger.from_crontab("* * * * *"))		# Every minute

		# Start the scheduler
		scheduler.start()

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
