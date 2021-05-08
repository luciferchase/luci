import discord
from discord.ext import commands

import psycopg2
import os

class Config(commands.Cog):
	"""Various commands to set up the bot in your server"""
	
	def __init__(self, bot):
		self.bot = bot

		# Set up database
		DATABASE_URL = os.environ["DATABASE_URL"]

		self.dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		self.cursor = self.dbcon.cursor()

		# Create config tables if not made earlier
		query = """CREATE TABLE IF NOT EXISTS schedule_meme(
				guild_id	BIGINT 		NOT NULL,
				channel_id	BIGINT		NOT NULL,
				state		BOOLEAN		NOT NULL)"""
		self.cursor.execute(query)

		query = """CREATE TABLE IF NOT EXISTS schedule_wallpaper(
				guild_id	BIGINT 		NOT NULL,
				channel_id	BIGINT		NOT NULL,
				state		BOOLEAN		NOT NULL)"""
		self.cursor.execute(query)

		query = """CREATE TABLE IF NOT EXISTS schedule_ipl(
				guild_id	BIGINT 		NOT NULL,
				channel_id	BIGINT		NOT NULL,
				state		BOOLEAN		NOT NULL)"""
		self.cursor.execute(query)
		self.dbcon.commit()