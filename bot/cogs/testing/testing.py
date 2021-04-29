import discord
from discord.ext import commands

import psycopg2

class Testing(commands.Cog):

	@commands.is_owner()
	@commands.command(hidden = True)
	def test(sel, ctx):
		DATABASE_URL = os.environ["DATABASE_URL"]

		dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		cursor = dbcon.cursor()

		query = """SELECT * FROM CONFIG"""
		cursor.execute(query)

		data = cursor.fetchall()
		await ctx.send(data)

		print(data)
		print(len(data))
		print(type(data))