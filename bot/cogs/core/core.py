import discord
from discord.ext import commands

import logging
import os
import psycopg2

class Core(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def ping(self, ctx) :
		await ctx.send(f"🏓 Pong with {str(round(bot.latency, 3))}")

	@commands.is_owner()
	@commands.command(hidden = True)
	async def sql(self, ctx, *query):
		log = logging.getLogger("sql")

		DATABASE_URL = os.environ["DATABASE_URL"]

		dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		cursor = dbcon.cursor()

		query = " ".join(query)
		print("Executing query:", query)
		try:
			cursor.execute(query)
			await ctx.send("Query executed successfully")
			try:
				dbcon.commit()
			except:
				pass
		except:
			log.error(f"{query} not executed successfully")
			await ctx.send("Query not executed. Check logs.")

		try:
			data = cursor.fetchall()
			print(data)
			await ctx.send(data)
		except:
			pass

	@commands.is_owner()
	@commands.command(hidden = True, aliases = ["status", "bs"])
	async def botstatus(self, ctx, *query):
		"""Set botstatus `luci <status> <activity> <text>`
		`status` can be: online[o], idle[i], dnd[d]
		`activity` can be : playing[p], listening[l], watching[w], competing[c]
		"""
		log = logging.getLogger("botstatus")

		status, activity, *text = query
		text = " ".join(text)

		DATABASE_URL = os.environ["DATABASE_URL"]

		dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		cursor = dbcon.cursor()

		query = """CREATE TABLE IF NOT EXISTS botstatus(
				status		TEXT	NOT NULL,
				activity 	TEXT,
				name 		TEXT)"""
		cursor.execute(query)
		dbcon.commit()

		cursor.execute("DELETE FROM botstatus")
		dbcon.commit()

		query = f"""INSERT INTO botstatus VALUES
				('{status}', '{activity}', '{text}')"""
		cursor.execute(query)
		dbcon.commit()

		if (status[0] == "o"):
			status_class = discord.Status.online
		elif (status[0] == "i"):
			status_class = discord.Status.idle
		elif (status[0] == "d"):
			status_class = discord.Status.dnd

		if (activity[0] == "p"):
			activity_type = discord.Game(name = text)
		elif (activity[0] == "l"):
			activity_type = discord.Activity(
					type = discord.ActivityType.listening,
					name = text
					)
		elif (activity[0] == "w"):
			activity_type = discord.Activity(
					type = discord.ActivityType.watching,
					name = text
					)
		elif (activity[0] == "c"):
			activity_type = discord.Activity(
					type = discord.ActivityType.competing,
					name = text
					)
		try:
			await self.bot.change_presence(
				status = status_class, 
				activity = activity_type
				)
			print("Activity set successfully")
			await ctx.send("Activity set successfully")
		except:
			log.warning("Cannot set activity")
			await ctx.send("Cannot set activity")

	@commands.is_owner()
	@commands.command(hidden = True)
	async def botname(self, ctx, name):
		"""Change bot name.
		   Syntax: `luci botname <name>`
		"""
		log = logging.getLogger("botname")
		try:
			await self.bot.user.edit(username = name)
			await ctx.send("Bot name changed successfully")
		except:
			log.error("Cannot change bot name")
			await ctx.send("Error. Bot name not changed. Check logs.")

	@commands.is_owner()
	@commands.command(hidden = True)
	async def botavatar(self, ctx):
		"""Change bot name.
		"""
		log = logging.getLogger("botavatar")
		with open("/app/bot/avatar.png", "rb") as avatar:
			try:
				await self.bot.user.edit(avatar = avatar)
				await ctx.send("Bot avatar chaned successfully")
			except:
				log.error("Cannot change bot name")
				await ctx.send("Error. Bot name not changed. Check logs.")
