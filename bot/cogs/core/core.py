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
		except:
			pass

	@commands.is_owner()
	@commands.command(hidden = True)
	async def botstatus(self, ctx, *query):
		pass