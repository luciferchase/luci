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

		embed = discord.Embed(
			color = 0x19f0e2,						# Cyan
			title = "Sattebaaz Championship",
		)
		embed.add_field(
			name = "Who do you think will win today's match?",
			value = ':regional_indicator_a: Chennai Super Kings \n:regional_indicator_b: Sunrisers Hyderabad'
		)
		# embed.set_thumbnail(url = self.ipl_logo)

		last_embed = await ctx.send(embed = embed)
		await last_embed.add_reaction("🇦")
		await last_embed.add_reaction("🇧")

		config[3] = last_embed.id
		query = """UPDATE CONFIG
					SET EMBED_ID = {}""".format(last_embed.id)
		cursor.execute(query)
		dbcon.commit()
