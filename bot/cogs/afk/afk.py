import discord
from discord.ext import commands

import os
import psycopg2

class AFK(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		# Get emojis
		self.ping_emoji = self.bot.get_emoji(839468910734606356)
		self.blobwave_emoji = self.bot.get_emoji(839737122633023498)
		self.nacho_emoji = self.bot.get_emoji(839499460874862655)
		self.check_emoji = self.bot.get_emoji(839713949436084246)

		# Set up database
		DATABASE_URL = os.environ["DATABASE_URL"]

		self.dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		self.cursor = self.dbcon.cursor()

		# Create table if not exists
		query = """CREATE TABLE IF NOT EXISTS afk(
				member_id 	BIGINT	NOT NULL 	PRIMARY KEY,
				message		TEXT,
				last_seen	TEXT	NOT NULL,
				guild_id	BIGINT 	NOT NULL)"""
		self.cursor.execute(query)
		self.dbcon.commit()

	@commands.Cog.listener("on_message")
	async def afk_message(self, ctx, message: discord.Message):
		# Return if the message is in the dm
		if (message.guild is None):
			return

		# Fetch all AFK members
		self.cursor.execute(f"""SELECT * FROM afk WHERE guild_id = {message.guild.id}""")
		data = self.cursor.fetchall()

		if (len(data) == 0):
			return

		for index in range(len(data)):
			afk_member = self.bot.get_user(data[index][0])

			# If an AFK member is pinged
			if (afk_member.mention in message.content):
				await ctx.send(f"{self.ping_emoji} :: {message.author.mention}, **{afk_member.nick}** is currently AFK. [Last seen {data[index][2]}]")

				# Send a reason if present
				if (data[index][1] != None):
					await ctx.send(f"**Reason:** {data[index][1]}")

			# If an AFK member sends a message
			if (message.author == afk_member):
				# Remove from database
				self.cursor.execute(f"""DELETE FROM afk WHERE member_id = {data[index][0]}""")
				self.dbcon.commit()

				# Change nickname
				# First get member instance of the user
				for member in self.bot.get_all_members():
					if (member.id == afk_member.id):
						await member.edit(nick = afk_member.nick[6:])

				# Send welcome message
				await ctx.send(f"{self.blobwave_emoji} :: Welcome back, {afk_member.mention}! I've removed your AFK status. Enjoy {self.nacho_emoji}")

	@commands.guild_only()
	@commands.command()
	async def afk(self, ctx, *message):
		"""Set yourself AFK.
		Usage: `luci afk [message [optional]]"""
		# Insert data into the database
		try:
			query = f"""INSERT INTO afk VALUES
					({ctx.author.id}, '{" ".join(message)}', '{datetime.now().strftime("%m/%d/%Y %H:%M:%S")}', {ctx.guild.id})"""
			self.cursor.execute(query)
			self.dbcon.commit()
		
		except:
			self.cursor.execute("DELETE FROM afk WHERE member_id = {}".format(ctx.author.id))
			self.dbcon.commit()

			await ctx.send(f"{self.blobwave_emoji} :: {ctx.author.mention} You are already set as AFK. Welcome back! {self.nacho_emoji}")
		
		if (message != None):
			await ctx.send(f"{self.check_emoji} :: {ctx.author.mention} I have set you as AFK. **Reason:** {' '.join(message)}")
		else:
			await ctx.send(f"{self.check_emoji} :: {ctx.author.mention} I have set you as AFK.")

		# Change nickname
		# First get member instance of the user
		for member in self.bot.get_all_members():
			if (member.id == ctx.author.id):
				await member.edit(nick = f"[AFK] {ctx.author.nick}")
