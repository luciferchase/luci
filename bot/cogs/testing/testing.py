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

		cursor.execute("DELETE FROM CONFIG")

		query = """INSERT INTO CONFIG VALUES
				(1, '2021-04-28', 1254079, 0, 0)"""
		cursor.execute(query)
		dbcon.commit()

		query = """INSERT INTO STANDINGS VALUES
				(707557256220115035, 30),
				(650661454000947210, 30)"""
		cursor.execute(query)
		dbcon.commit()

		query = """SELECT * FROM STANDINGS"""
		cursor.execute(query)

		data = cursor.fetchall()
		await ctx.send(data)

		print(data)
		print(len(data))
		print(type(data))