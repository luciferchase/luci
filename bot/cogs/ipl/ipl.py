import discord
from discord.ext import commands

import os
import psycopg2
import requests

class IPL(commands.Cog):
	"""View details of matches and play Sattebaaz Championship"""
	
	@commands.is_owner()
	@commands.command(hidden = True)
	async def database(self, ctx):
		DATABASE_URL = os.environ['DATABASE_URL']

		dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		cursor = dbcon.cursor()

		query = """CREATE TABLE IF NOT EXISTS CONFIG(
				RATE_LIMIT 		INT 	NOT NULL,
				LAST_SYNCED		TEXT	NOT NULL,
				LAST_MATCH_ID	INT 	NOT NULL,
				EMBED_ID		BIGINT 	NOT NULL,
				CHANNEL_ID 		BIGINT 	NOT NULL)
				"""
		cursor.execute(query)

		query = """CREATE TABLE IF NOT EXISTS STANDINGS(
				USER_ID			BIGINT 	NOT NULL,
				POINTS			INT 	NOT NULL)"""
		cursor.execute(query)

		query = """CREATE TABLE IF NOT EXISTS MATCHES(
				UNIQUE_ID		INT 	NOT NULL,
				TEAM_1			TEXT	NOT NULL,
				TEAM_2			TEXT 	NOT NULL,
				WINNER_TEAM		TEXT,
				MATCH_STARTED	BOOLEAN NOT NULL)"""
		cursor.execute(query)
		dbcon.commit()
		
		print("All tables created successfully")

		query = """INSERT INTO CONFIG VALUES
				(0, '2021-04-29', 1254080, 0, 0)"""
		cursor.execute(query)

		query = """SELECT * FROM CONFIG"""
		cursor.execute(query)
		data = cursor.fetchall()

		await ctx.send(data)