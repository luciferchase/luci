# Install all dependencies
import discord
from discord.ext import commands
from pretty_help import DefaultMenu, PrettyHelp

import sys
import os
import logging
import requests
import psycopg2

# Install all cogs
from cogs.aki import aki
from cogs.avatar import avatar
from cogs.comics import comics
from cogs.core import core, botstatus, schedule_jobs
from cogs.conversationgames import conversationgames
from cogs.ipl import ipl
from cogs.math import math
from cogs.meme import meme
from cogs.photo import photo
# from cogs.testing import testing

# Get Members intent
intents = discord.Intents.all()

# Configure the bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = commands.Bot(command_prefix = ["luci ", "Luci "], case_insensitive = True, strip_after_prefix = True, 
	intents = intents, self_bot = False, owner_id = 707557256220115035,  
	help_command = PrettyHelp(color = 0xf34949, sort_commands = True),
	description = "A General-Purpose Discord Bot Created by luciferchase#6310")

# Set up logging
logging.basicConfig(level = logging.WARNING)

# Register Cogs
bot.add_cog(aki.Aki(bot))
bot.add_cog(avatar.Avatar())
bot.add_cog(botstatus.Botstatus(bot))
bot.add_cog(comics.Comics(bot))
bot.add_cog(core.Core(bot))
# bot.add_cog(core.Help(bot))
bot.add_cog(conversationgames.ConversationGames())
bot.add_cog(ipl.IPL(bot))
bot.add_cog(math.Math(bot))
bot.add_cog(meme.Meme())
bot.add_cog(photo.Photo())
# bot.add_cog(testing.Testing())

<<<<<<< HEAD
# Start scheduled commands
scheduler = schedule_jobs.Scheduler(bot).schedule()
scheduler.start()
=======
# Scheduled events
async def schedule_meme():
	channel = bot.get_channel(835113922172026881)
	embed = await meme.Meme().meme_code()
	meme_embed = await channel.send(embed = embed)
	await meme_embed.add_reaction("😂")

# Only a small function so leaving it here
async def schedule_wallpaper():
	channel = bot.get_channel(738731755569414197)
	api = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-IN"

	response = requests.get(api)
	data = response.json()

	await channel.send(data["images"][0]["title"])
	
	wallpaper = await channel.send(f'http://bing.com{data["images"][0]["url"]}')
	await wallpaper.add_reaction("❤️")
	await wallpaper.add_reaction("👍")
	await wallpaper.add_reaction("👎")

async def schedule_ipl():
	channel = bot.get_channel(756701639544668160)
	IPL = ipl.IPL(bot)

	# Update points and display last winners
	embed = await IPL.show_points()
	await channel.send(embed = embed)

	# Show current standings
	embed = await IPL.fetch_standings()
	await channel.send(embed = embed)

	# Make polls for todays match
	*_, next_match_details, next_match_details_2 = IPL.fetch_matches()

	channel = bot.get_channel(756701639544668160)

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

# Core Commands
@bot.event	
async def on_ready():
	print("Connected to discord")

	log = logging.getLogger("on_ready")

	# Change botstatus from datatbase
	try:
		cursor.execute("SELECT * FROM botstatus")
		data = cursor.fetchall()
	except:
		data = []

	if (len(data) != 0):
		data = data[0]

		if (data[0] == "o"):
			status_class = discord.Status.online
		elif (data[0] == "i"):
			status_class = discord.Status.idle
		elif (data[0] == "d"):
			status_class = discord.Status.dnd

		if (data[1] == "p"):
			activity_type = discord.Game(name = data[2])
		elif (data[1] == "l"):
			activity_type = discord.Activity(
				type = discord.ActivityType.listening,
				name = data[2]
				)
		elif (data[1] == "w"):
			activity_type = discord.Activity(
				type = discord.ActivityType.watching,
				name = data[2]
				)
		elif (data[1] == "c"):
			activity_type = discord.Activity(
				type = discord.ActivityType.competing,
				name = data[2]
				)
	else:
		status_class = discord.Status.idle
		activity_type = discord.Activity(
			type = discord.ActivityType.watching,
			name = "your cute smile"
			)
	
	try:
		await bot.change_presence(status = status_class, activity = activity_type)
		print("Activity set successfully")
	except:
		log.warning("Cannot set activity")
	
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
	scheduler.add_job(schedule_meme, CronTrigger.from_crontab("30 * * * *")) # Every hour

	# Because we are 05:30 hrs ahead of GMT, every cron is set 05:30 hrs behind
	scheduler.add_job(schedule_wallpaper, CronTrigger.from_crontab("30 02 * * *")) # Each day at 0800 hrs
	scheduler.add_job(schedule_ipl, CronTrigger.from_crontab("30 02 * * *"))

	# Start the scheduler
	scheduler.start()

@bot.event
async def on_member_join(member):
	channel = member.guild.system_channel
		
	if channel is not None:
		await channel.send(f"@{member.mention}")
		embed = discord.Embed(
			title = f"Welcome {member.name}", 
			description = f"Aap aayen hai {member.guild.name} ki bagiyaaan mein \n"
							"phool khile hai gulshan gulshan \n"
							"Phulllll khile hai gulshan gulshaannnnnnnnn \n"
							"Phool khile hai iss bagiyaan mein \n"
							"Aap aayein hai gulshan gulshan"
		) 
		embed.set_thumbnail(url = member.guild.icon_url)
		embed.set_image(url = member.avatar_url)
		await channel.send(embed = embed)

@bot.event
async def on_member_remove(member):
	channel = member.guild.system_channel
		
	if channel is not None:
		embed = discord.Embed(
			title = "Sed lyf",
			description = f"{member.name} has left {member.guild.name} 🥺"
		)
		embed.set_thumbnail(url = member.guild.icon_url)
		embed.set_image(url = member.avatar_url)
		await channel.send(embed = embed)

@bot.event
async def on_invite_create(invite):
	# Fetch dm id to me
	dm = await create_dm(707557256220115035)

	embed = discord.Embed(
		title = f"Invite Created by {invite.inviter}",
		description = f"Channel: {invite.channel}"
						f"Used so far: {invite.uses}"
	)
	await dm.send(embed = embed)

# Add last 5 deleted message to database
@bot.event
async def on_message_delete(message):
	query = """CREATE TABLE IF NOT EXISTS snipe(
			mssg TEXT NOT NULL,
			author	TEXT NOT NULL)"""
	cursor.execute(query)
	dbcon.commit()

	# FIFO - Removes the first message from end and adds the new message to the top of the stack
	cursor.execute("SELECT * FROM snipe")
	data = cursor.fetchall()

	print(message.content, message.author.id)

	# Check if there are more than 5 messages in the database
	if (len(data) >= 5):
		# Remove the oldest message
		del data[0]

		# Add new message to the top of the stack
		mssg, author = message.content, message.author.id
		data.append((mssg, author))
	else:
		mssg, author = message.content, message.author.id
		data.append((mssg, author))

	# Update database
	cursor.execute("DELETE FROM snipe")
	cursor.execute("INSERT INTO snipe VALUES {}".format(data))
>>>>>>> 305ffdfb871250926fc42b2860bc2e52c431760d

# Run the bot
bot.run(BOT_TOKEN)
