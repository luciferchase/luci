# Install all dependencies
import discord
from discord.ext import commands

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import sys
import os
import logging

# Install all cogs
from cogs.aki import aki
from cogs.avatar import avatar
from cogs.comics import comics
from cogs.conversationgames import conversationgames
from cogs.forward import forward
from cogs.ipl import ipl
from cogs.math import math
from cogs.meme import meme
from cogs.photo import photo

# Get Members intent
intents = discord.Intents.all()

# Configure the bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = commands.Bot(command_prefix = "luci ", case_insensitive = True, intents = intents)

logging.basicConfig(level = logging.WARNING)

# Register Cogs
bot.add_cog(aki.Aki(bot))
bot.add_cog(avatar.Avatar())
bot.add_cog(comics.Comics(bot))
bot.add_cog(conversationgames.ConversationGames())
bot.add_cog(forward.Forward(bot))
bot.add_cog(ipl.IPL(bot))
bot.add_cog(math.Math(bot))
bot.add_cog(meme.Meme())
bot.add_cog(photo.Photo())

# # Scheduled events
# async def schedule_meme():
# 	await meme.Meme().meme()


# Core Commands
@bot.event	
async def on_ready():
	log = logging.getLogger("on_ready")

	try:
		await bot.change_presence(
			status = discord.Status.idle, 
			activity = discord.Activity(
				type = discord.ActivityType.listening,
				name = "your heartbeats"
				)
			)
		print("Activity set successfully")
	except:
		log.warning("Cannot set activity")
	
	print("Connected to discord")

	# Initialize scheduler
	schedule_log = logging.getLogger("apscheduler")
	schedule_log.setLevel(logging.WARNING)

	job_defaults = {
		"coalesce": True,  # Multiple missed triggers within the grace time will only fire once
		"max_instances": 5,  # This is probably way too high, should likely only be one
		"misfire_grace_time": 15,  # 15 seconds ain't much, but it's honest work
		"replace_existing": True,  # Very important for persistent data
	}

	scheduler = AsyncIOScheduler(job_defaults = job_defaults, logger = schedule_log)

	# Add jobs to scheduler
	scheduler.add_job(meme.Meme().meme, CronTrigger.from_crontab("* * * * *"))		# Every minute

	# Start the scheduler
	scheduler.start()

@bot.event
async def on_member_join(member):
	channel = member.guild.system_channel
		
	if channel is not None:
		embed = discord.Embed(
			title = f"Welcome @{member.name}", 
			description = f"Ayeeeee! Welcome to {member.guild.name} 😁😁"
		) 
		embed.set_thumbnail(url = member.avatar_url) 
		await channel.send(embed = embed)

@commands.command()
async def ping(ctx) :
	await ctx.send(f"🏓 Pong with {str(round(bot.latency, 3))}")


# Run the bot
bot.run(BOT_TOKEN)