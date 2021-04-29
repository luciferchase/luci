import discord
from discord.ext import commands

import os
import psycopg2
import requests
from datetime import datetime, date

class IPL(commands.Cog):
	"""View details of matches and play Sattebaaz Championship"""

	def __init__(self, bot):
		self.bot = bot

		DATABASE_URL = os.environ["DATABASE_URL"]

		self.dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		self.cursor = self.dbcon.cursor()

		query = """SELECT * FROM CONFIG"""
		self.cursor.execute(query)

		self.config = self.cursor.fetchall()

		self.api_matches = "https://cricapi.com/api/matches"
			
	@commands.is_owner()
	@commands.command(hidden = True)
	async def database(self, ctx):

		query = """CREATE TABLE IF NOT EXISTS CONFIG(
				RATE_LIMIT 		INT 	NOT NULL,
				LAST_SYNCED		DATE	NOT NULL,
				LAST_MATCH_ID	INT 	NOT NULL,
				EMBED_ID		BIGINT 	NOT NULL,
				CHANNEL_ID 		BIGINT 	NOT NULL)
				"""
		self.cursor.execute(query)

		query = """CREATE TABLE IF NOT EXISTS STANDINGS(
				USER_ID			BIGINT 	NOT NULL,
				POINTS			INT 	NOT NULL)"""
		self.cursor.execute(query)

		query = """CREATE TABLE IF NOT EXISTS LAST_MATCH(
				UNIQUE_ID		INT 	NOT NULL,
				TEAM_1			TEXT	NOT NULL,
				TEAM_2			TEXT 	NOT NULL,
				WINNER_TEAM		TEXT	NOT NULL)"""
		self.cursor.execute(query)
		self.dbcon.commit()

		query = """CREATE TABLE IF NOT EXISTS UPCOMING_MATCH(
				UNIQUE_ID		INT 	NOT NULL,
				TEAM_1			TEXT	NOT NULL,
				TEAM_2			TEXT 	NOT NULL,
				MATCH_STARTED	BOOLEAN NOT NULL)"""
		self.cursor.execute(query)
		self.dbcon.commit()
			
		print("All tables created successfully")

	@commands.is_owner()
	@commands.command(hidden = True)
	async def insert(self, ctx):
		print(self.config)
	
		if (date.today() > self.config[1]):
			params = {
				"apikey": os.environ("CRIC_API_KEY")
			}
			response = requests.get(self.api_matches, params = params).json()["matches"]

