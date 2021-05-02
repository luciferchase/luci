import discord
from discord.ext import commands

import logging
import os
import psycopg2


class Botstatus(commands.Cog):
	"""Set up status of bot"""
	def __init__(self, bot):
		self.bot = bot
		self.log = logging.getLogger("botstatus")

		# Set up database
		DATABASE_URL = os.environ["DATABASE_URL"]

		self.dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		self.cursor = self.dbcon.cursor()

		# Wait untll all the bot's internal workings are all caught up
		await self.bot.wait_until_ready()

		# Change botstatus from datatbase
		try:
			self.cursor.execute("SELECT * FROM botstatus")
			data = self.cursor.fetchall()
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
				activity_type = discord.Activity(type = discord.ActivityType.listening, name = data[2])
			elif (data[1] == "w"):
				activity_type = discord.Activity(type = discord.ActivityType.watching, name = data[2])
			elif (data[1] == "c"):
				activity_type = discord.Activity(type = discord.ActivityType.competing, name = data[2])
		
		# Default status
		else:
			status_class = discord.Status.idle
			activity_type = discord.Activity(type = discord.ActivityType.watching, name = "your cute smile")

		try:
			await self.bot.change_presence(status = status_class, activity = activity_type)
			print("Activity set successfully")
		except:
			self.log.warning("Cannot set activity")

	@commands.is_owner()
	@commands.command(hidden = True, aliases = ["status", "bs"])
	async def botstatus(self, ctx, *query):
		"""Set botstatus `luci <status> <activity> <text>`
		`status` can be: online[o], idle[i], dnd[d]
		`activity` can be : playing[p], listening[l], watching[w], competing[c]
		"""
		status, activity, *text = query
		text = " ".join(text)

		query = """CREATE TABLE IF NOT EXISTS botstatus(
				status		TEXT	NOT NULL,
				activity 	TEXT,
				name 		TEXT)"""
		self.cursor.execute(query)
		self.dbcon.commit()

		self.cursor.execute("DELETE FROM botstatus")
		self.dbcon.commit()

		try:
			query = f"""INSERT INTO botstatus VALUES
					('{status}', '{activity}', '{text}')"""
			self.cursor.execute(query)
			self.dbcon.commit()
		except:
			await ctx.send("Cannot add it status to database. Check logs.")
			self.log.warning("Cannot add status to database.")

		if (status[0] == "o"):
			status_class = discord.Status.online
		elif (status[0] == "i"):
			status_class = discord.Status.idle
		elif (status[0] == "d"):
			status_class = discord.Status.dnd

		if (activity[0] == "p"):
			activity_type = discord.Game(name = text)
		elif (activity[0] == "l"):
			activity_type = discord.Activity(type = discord.ActivityType.listening, name = text)
		elif (activity[0] == "w"):
			activity_type = discord.Activity(type = discord.ActivityType.watching, name = text)
		elif (activity[0] == "c"):
			activity_type = discord.Activity(type = discord.ActivityType.competing, name = text)
		
		try:
			await self.bot.change_presence(status = status_class, activity = activity_type)
			print("Activity set successfully")
			await ctx.send("Activity set successfully")
		except:
			self.log.warning("Cannot set activity")
			await ctx.send("Cannot set activity")

