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
			dbcon.commit()
			await ctx.send("Query executed successfully")
		except:
			log.error(f"{query} not executed successfully")
			await ctx.send("Query not executed. Check logs.")

		try:
			data = cursor.fetchall()
			print(data)
			await query.author.send(data)
		except:
			pass

	@commands.is_owner()
	@commands.command(hidden = True)
	async def botstatus(self, ctx, *query):
		"""Set botstatus `luci <status> <activity> <text>`
		`status` can be: online[o], idle[i], dnd[d]
		`activity` can be : playing[p], listening[l], watching[w], competing[c]
		"""
		status, activity, text = query
		text = " ".join(text)

		if (status[0] == "o"):
			status = discord.Status.online
		elif (status[0] == "i"):
			status = discord.Status.idle
		elif (status[0] == "d"):
			status = discord.Status.dnd

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
			await bot.change_presence(
				status = status, 
				activity = activity_type
				)
			print("Activity set successfully")
		except:
			log.warning("Cannot set activity")
			await query.author.send("Cannot set activity")