import discord
from discord.ext import commands

import psycopg2
import os
from datetime import date, timedelta

class Testing(commands.Cog):

	@commands.is_owner()
	@commands.command(hidden = True)
	async def test(sel, ctx):
		DATABASE_URL = os.environ["DATABASE_URL"]

		dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		cursor = dbcon.cursor()

		query = f"""INSERT INTO CONFIG VALUES
				(0, {date.today() - timedelta(days = 1)}, 1254079, 0, 0)"""
		cursor.execute(query)
		dbcon.commit()

		query = """SELECT * FROM CONFIG"""
		cursor.execute(query)

		data = cursor.fetchall()
		await ctx.send(data)

		print(data)
		print(len(data))
		print(type(data))