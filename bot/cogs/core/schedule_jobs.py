import discord
from discord.ext import commands

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import logging
import os
import psycopg2
import requests

from cogs.meme import meme
from cogs.ipl import ipl

class Scheduler(commands.Cog):
	"""Schedule commands."""
	def __init__(self, bot):
		self.bot = bot
	
	# Scheduled events
	async def schedule_meme(self):
		channel = self.bot.get_channel(835113922172026881)
		embed = await meme.Meme().meme_code()
		meme_embed = await channel.send(embed = embed)
		await meme_embed.add_reaction("😂")

	# Only a small function so leaving it here
	async def schedule_wallpaper(self):
		channel = self.bot.get_channel(738731755569414197)
		api = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"

		response = requests.get(api)
		data = response.json()

		await channel.send(data["images"][0]["title"])
		
		wallpaper = await channel.send(f'http://bing.com{data["images"][0]["url"]}')
		await wallpaper.add_reaction("❤️")
		await wallpaper.add_reaction("👍")
		await wallpaper.add_reaction("👎")

	async def schedule_ipl(self):
		# Set up database
		DATABASE_URL = os.environ["DATABASE_URL"]

		dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		cursor = dbcon.cursor()

		# Get Channel
		channel = self.bot.get_channel(756701639544668160)
		IPL = ipl.IPL(self.bot)

		# Update points and display last winners
		embed = await IPL.show_points()
		await channel.send(embed = embed)

		# Show current standings
		embed = await IPL.fetch_standings()
		await channel.send(embed = embed)

		# Make polls for todays match
		*_, next_match_details, next_match_details_2 = IPL.fetch_matches()

		channel = self.bot.get_channel(756701639544668160)

		allowed_mentions = discord.AllowedMentions(everyone = True)
		await channel.send(content = "@everyone", allowed_mentions = allowed_mentions)

		embed_id = await IPL.predict_code(next_match_details)

		# Update database
		cursor.execute("DELETE FROM predict")
		query = """INSERT INTO predict VALUES
				({})""".format(embed_id)
		cursor.execute(query)
		dbcon.commit()

		# If there is a second match on that day
		if (next_match_details_2 != False):
			embed_id = await IPL.predict_code(next_match_details_2)

			# Update database
			query = """INSERT INTO predict VALUES
					({})""".format(embed_id)
			cursor.execute(query)
			dbcon.commit()

	def schedule(self):
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
		scheduler.add_job(self.schedule_meme, CronTrigger.from_crontab("30 * * * *")) # Every hour

		# Because we are 05:30 hrs ahead of GMT, every cron is set 05:30 hrs behind
		scheduler.add_job(self.schedule_wallpaper, CronTrigger.from_crontab("30 02 * * *")) # Each day at 0800 hrs
		scheduler.add_job(self.schedule_ipl, CronTrigger.from_crontab("30 02 * * *"))

		# Start the scheduler
		return scheduler
