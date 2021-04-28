import discord
from discord.ext import commands

import os
import psycopg2
import requests

class Testing(commands.Cog):
	
	@commands.is_owner()
	@commands.command(hidden = True):
	async def database(self):
		DATABASE_URL = os.environ['DATABASE_URL']

		dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		cursor = dbcon.cursor()

		query = """CREATE TABLE CONFIG IF NOT EXISTS(
				RATE_LIMIT 		INT 	NOT NULL,
				LAST_SYNCED		TEXT	NOT NULL,
				LAST_MATCH_ID	INT 	NOT NULL,
				EMBED_ID		BIGINT 	NOT NULL,
				CHANNEL_ID 		BIGINT 	NOT NULL)
				"""
		cursor.execute(query)

		query = """CREATE TABLE STANDINGS IF NOT EXISTS(
				USER_ID			BIGINT 	NOT NULL,
				POINTS			INT 	NOT NULL)"""
		cursor.execute(query)

		query = """CREATE TABLE MATCHES IF NOT EXISTS(
				UNIQUE_ID		INT 	NOT NULL,
				TEAM_1			TEXT	NOT NULL,
				TEAM_2			TEXT 	NOT NULL,
				WINNER_TEAM		TEXT	NOT NULL)"""
		cursor.execute(query)
		cursor.commit()
		
		print("All tables created successfully")

		query = """INSERT INTO CONFIG VALUES
				(4, '2021-04-28', 1254079, 0, 0)"""
		cursor.execute(query)

		query = """INSERT INTO STANDINGS VALUES
				(650661454000947210, 20),
				(707557256220115035, 30)"""
		cursor.execute(query)

		try:
			response = requests.get("https://cricapi.com/api/cricketScore?apikey=31AeMD7w58VL5uUQxEguPqwpwSg2&unique_id=1034809")
			matches = [match for match in response.json()["matches"] if match["unique_id"] == 1254079][0]

			query = f"""INSERT INTO MATCHES VALUES
					({matches["unique_id"]}, {matches["team-1"]}, {matches["team-2"]}, {matches["winner_team"]}"""
			cursor.execute(query)
		except:
			print("Rate limit hit")

		print("All data inserted")
		cursor.commit()

		query = """SELECT * FROM CONFIG"""
		cursor.execute(query)
		data = cursor.fetchall()

		await ctx.send(data)

		query = """SELECT * FROM STANDINGS"""
		cursor.execute(query)
		data = cursor.fetchall()

		await ctx.send(data)
