import discord
from discord.ext import commands

import os
import psycopg2
import requests
from datetime import datetime, date

class IPL(commands.Cog):
	"""View details of matches and play Sattebaaz Championship"""

	def __init__(self):
		DATABASE_URL = os.environ["DATABASE_URL"]

		self.dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		self.cursor = dbcon.cursor()

		query = """SELECT * FROM CONFIG"""
		self.cursor.execute(query)

		self.config = self.cursor.fetchall()[0]

		self.api_matches = "https://cricapi.com/api/matches"
			
	@commands.is_owner()
	@commands.command(hidden = True)
	async def database(self, ctx):

		query = """CREATE TABLE IF NOT EXISTS CONFIG(
				RATE_LIMIT 		INT 	NOT NULL,
				LAST_SYNCED		TEXT	NOT NULL,
				LAST_MATCH_ID	INT 	NOT NULL,
				EMBED_ID		BIGINT 	NOT NULL,
				CHANNEL_ID 		BIGINT 	NOT NULL)
				"""
		self.cursor.execute(query)

		query = """CREATE TABLE IF NOT EXISTS STANDINGS(
				USER_ID			BIGINT 	NOT NULL,
				POINTS			INT 	NOT NULL)"""
		self.cursor.execute(query)

		query = """CREATE TABLE IF NOT EXISTS MATCHES(
				UNIQUE_ID		INT 	NOT NULL,
				TEAM_1			TEXT	NOT NULL,
				TEAM_2			TEXT 	NOT NULL,
				WINNER_TEAM		TEXT,
				MATCH_STARTED	BOOLEAN NOT NULL)"""
		self.cursor.execute(query)
		self.dbcon.commit()
		
		print("All tables created successfully")

	@commands.is_owner()
	@commands.command(hidden = True)
	async def insert(self, ctx):
		if (date.today() > self.config[1]):
			params = {
				"apikey": os.environ("CRIC_API_KEY")
			}
			response = requests.get(self.api_matches, params = params).json()["matches"]

	