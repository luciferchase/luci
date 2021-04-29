import discord
from discord.ext import commands

import os
import psycopg2
import requests
from datetime import datetime, date
import calendar

class IPL(commands.Cog):
	"""View details of matches and play Sattebaaz Championship"""

	def __init__(self, bot):
		self.bot = bot

		DATABASE_URL = os.environ["DATABASE_URL"]

		self.dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		self.cursor = self.dbcon.cursor()

		self.cursor.execute("SELECT * FROM CONFIG")
		self.config = list(self.cursor.fetchall()[0])
		
		self.cursor.execute("SELECT * FROM STANDINGS")
		self.standings = list(self.cursor.fetchall())

		self.api_matches = "https://cricapi.com/api/matches"
		self.params_matches = {
			"apikey": os.getenv("CRIC_API_KEY")
		}

		self.api_score = "https://cricapi.com/api/cricketScore"
		self.params_score = {
			"apikey": os.getenv("CRIC_API_KEY"),
			"unique_id": self.config[2]
		}
		
		if (str(date.today()) > self.config[1]):
			self.config[0] = 1
			self.config[1] = date.today()
			self.config[2] += 1

			query = f"""UPDATE CONFIG SET
						RATE_LIMIT = {self.config[0]},
						LAST_SYNCED = {self.config[1]},
						LAST_MATCH_ID = {self.config[2]}
						"""
			self.cursor.execute(query)
			self.dbcon.commit()

			response = requests.get(self.api_matches, params = self.params_matches).json()
			self.last_match_details = [match for match in response["matches"] \
			if match["unique_id"] == self.config[2]]

			self.cursor.execute("DELETE FROM LAST_MATCH")

			query = f"""INSERT INTO LAST_MATCH VALUES
					({self.last_match_details[0]}, \
					{self.last_match_details[1]}, {self.last_match_details[2]}, \
					{self.last_match_details[3]})"""
			self.cursor.execute(query)

			for match in response["matches"]:
				if (match["unique_id"] == self.config[2] + 1):
					self.upcoming_match_details = match

					self.cursor.execute("DELETE FROM UPCOMING_MATCH")

					query = f"""INSERT INTO UPCOMING_MATCH VALUES
							({self.upcoming_match_details[0]}, \
							{self.upcoming_match_details[1]}, {self.upcoming_match_details[2]}, \
							{self.upcoming_match_details[3]})"""
					self.cursor.execute(query)
					self.dbcon.commit()	
			
				elif (match["unique_id"] == self.config[2] + 2):

					self.config[2] += 1

					query = f"""UPDATE CONFIG
								SET LAST_MATCH_ID = {self.confg[2]}"""
					self.cursor.execute(query)
					self.dbcon.commit()

					self.upcoming_match_details_2 = match

					query = f"""INSERT INTO UPCOMING_MATCH VALUES
							({self.upcoming_match_details_2[0]}, \
							{self.upcoming_match_details_2[1]}, {self.upcoming_match_details_2[2]}, \
							{self.upcoming_match_details_2[3]})"""
					self.cursor.execute(query)
					self.dbcon.commit()

		self.cursor.execute("SELECT * FROM LAST_MATCH")
		self.last_match_details = self.cursor.fetchall()[0]

		self.cursor.execute("SELECT * FROM UPCOMING_MATCH")
		data = self.cursor.fetchall()

		self.upcoming_match_details = data[0]
		self.upcoming_match_details_2 = False
		if (len(data) == 2):
			self.upcoming_match_details_2 = data[1]

		self.dog_api = "https://api.thedogapi.com/v1/images/search"

		self.image_url = {
			"Kolkata Knight Riders": "https://hdsportsnews.com/wp-content/uploads/2020/01/kolkata-knight-riders-kkr-2020-team-squad-players-live-score-time-table-point-table-schedule-auction-match-fixture-venue-highlight-1280x720.jpg",			
			"Rajasthan Royals": "https://cdn5.newsnationtv.com/images/2021/02/22/royal-rajasthan-logo-70.jpg",			
			"Royal Challengers Bangalore": "https://english.sakshi.com/sites/default/files/article_images/2020/11/8/RCB-Logo_571_855-1604821493.jpg",			
			"Mumbai Indians": "https://static.india.com/wp-content/uploads/2017/03/mumbai.jpg?impolicy=Medium_Resize&w=1200&h=800",			
			"Punjab Kings": "https://awaj.in/wp-content/uploads/2021/03/20210317_222651.jpg",			
			"Sunrisers Hyderabad": "https://2.bp.blogspot.com/-6cAZUQMFCqc/WwKFUZrPPmI/AAAAAAAACcM/TryzryihpEkoOMd6htpE8LjIH1r02FWSgCLcBGAs/s1600/SRH.jpg",			
			"Chennai Super Kings": "https://i.pinimg.com/originals/85/52/f8/8552f811e95b998d9505c43a9828c6d6.jpg",			
			"Delhi Capitals": "https://d3pc1xvrcw35tl.cloudfront.net/ln/images/686x514/teamsinnerintrodc534x432-resize-534x432-a7542dd51f-d979030f10e79596_202009106828.jpeg"
		}

		self.ipl_logo = "https://img.etimg.com/thumb/width-1200,height-900,imgsize-121113,resizemode-1,msid-81376248/ipl-2021-from-april-9-six-venues-no-home-games-no-spectators.jpg"


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
		
		await ctx.send("All tables created successfully")	

	@commands.bot_has_permissions(embed_links = True)
	@commands.command()
	async def ipl(self, ctx):
		""" Get details of last match played, winner and the next match
		"""

		embed = discord.Embed(
			color = 0x25dbf4,					# Blue
			title = "Matches",
		)
		embed.add_field(
			name = "Next Match", 
			value = f'{self.upcoming_match_details[1]} \nvs \
			\n{self.upcoming_match_details[2]}',
			inline = False
		)
		if (upcoming_match_details_2):
			embed.add_field(
			name = "Match 2", 
			value = f'{self.upcoming_match_details_2[1]} \nvs \
			\n{self.upcoming_match_details_2[2]}',
			inline = False
			)
		embed.add_field(
			name = "Last Match",
			value = f'{self.last_match_details[1]} \nvs \n{self.last_match_details[2]}',
			inline = True
		)
		embed.add_field(
			name = "Winner",
			value = f'{self.last_match_details[3]}',
			inline = True
		)
		embed.set_image(url = self.image_url[self.last_match_details[3]])
		embed.set_thumbnail(url = self.ipl_logo)
		await ctx.send(embed = embed)

	async def fetch_standings(self, ctx):
		self.cursor.execute("SELECT * FROM STANDINGS")
		data = self.cursor.fetchall()

		current_standings = {}

		for user in data:
			username = await self.bot.fetch_user(user[0])
			current_standings[username] = user[1]

		embed_string_name = ""
		embed_string_points = ""
		for user in current_standings:
			embed_string_name += f"\n{user}\n"
			embed_string_points += f"\n : \t {current_standings[user]}\n"

		embed = discord.Embed(
			color = 0x07f223,							# Green
			title = "Sattebaaz Championship",
		)
		embed.add_field(
			name = "Current Standings",
			value = f"```\n{embed_string_name}```",
			inline = True
		)
		embed.add_field(
			name = "Points",
			value = f"```\n{embed_string_points}```",
			inline = True
		)
		embed.set_thumbnail(url = self.ipl_logo)
		await ctx.send(embed = embed)

	@commands.bot_has_permissions(embed_links = True)
	@commands.is_owner()
	@commands.command(hidden = True)
	async def predict(self, ctx, match = 1):
		""" Poll for today's match
		"""

		allowed_mentions = discord.AllowedMentions(everyone = True)
		await ctx.send(content = "@everyone", allowed_mentions = allowed_mentions)

		if (match == 2):
			self.upcoming_match_details = self.upcoming_match_details_2

			channel = self.bot.get_channel(self.config_data[4])
			last_embed = await channel.fetch_message(self.config_data[3])
			emoji_a = []
			emoji_b = []
			winners = []
			for reaction in last_embed.reactions:
				async for user in reaction.users():
					if (reaction.emoji == "🇦" and not user.bot):
						emoji_a.append(user.id)
					elif (reaction.emoji == "🇧" and not user.bot):
						emoji_b.append(user.id)

			if (self.last_match_details[3] == self.last_match_details[1]):
				for user in emoji_a:
					query = """UPDATE STANDINGS
								SET POINTS = POINTS + 10
								WHERE USER_ID = {}""".format(user.id)
					self.cursor.execute(query)
					self.dbcon.commit()

					username = await self.bot.fetch_user(user)
					winners.append(username)
			else:
				for user in emoji_b:
					query = """UPDATE STANDINGS
								SET POINTS = POINTS + 10
								WHERE USER_ID = {}""".format(user.id)
					self.cursor.execute(query)
					self.dbcon.commit()
					
					username = await self.bot.fetch_user(user)
					winners.append(username)

		await fetch_standings()

		embed = discord.Embed(
			color = 0x19f0e2,						# Cyan
			title = "Sattebaaz Championship",
		)
		embed.add_field(
			name = "Who do you think will win today's match?",
			value = f':regional_indicator_a: {self.upcoming_match_details[1]}\n\
			:regional_indicator_b: {self.upcoming_match_details[2]}'
		)
		embed.set_thumbnail(url = self.ipl_logo)

		last_embed = await ctx.send(embed = embed)
		await last_embed.add_reaction("🇦")
		await last_embed.add_reaction("🇧")

		self.config[3] = last_embed.id
		query = """UPDATE CONFIG
					SET EMBED_ID = {}""".format(last_embed.id)
		self.cursor.execute(query)
		self.dbcon.commit()

	@commands.bot_has_permissions(embed_links = True)
	@commands.is_owner()
	@commands.command(hidden = True)
	async def points(self, ctx):
		""" Update Standings for Sattebaaz Championship
		"""

		channel = self.bot.get_channel(self.config_data[4])
		last_embed = await channel.fetch_message(self.config_data[3])
		emoji_a = []
		emoji_b = []
		winners = []
		for reaction in last_embed.reactions:
			async for user in reaction.users():
				if (reaction.emoji == "🇦" and not user.bot):
					emoji_a.append(user.id)
				elif (reaction.emoji == "🇧" and not user.bot):
					emoji_b.append(user.id)

		if (self.last_match_details[3] == self.last_match_details[1]):
			for user in emoji_a:
				query = """UPDATE STANDINGS
							SET POINTS = POINTS + 10
							WHERE USER_ID = {}""".format(user.id)
				self.cursor.execute(query)
				self.dbcon.commit()

				username = await self.bot.fetch_user(user)
				winners.append(username)
		else:
			for user in emoji_b:
				query = """UPDATE STANDINGS
							SET POINTS = POINTS + 10
							WHERE USER_ID = {}""".format(user.id)
				self.cursor.execute(query)
				self.dbcon.commit()
				
				username = await self.bot.fetch_user(user)
				winners.append(username)

		embed = discord.Embed(
			color = 0x07f223,						# Green
			title = "Sattebaaz Championship",
		)
		embed.add_field(
			name = "Last match was won by ...",
			value = self.last_match_details["winner_team"],
			inline = False
		)
		embed.add_field(
			name = "Winning sattebaaz",
			value = "`{}`".format("\n".join(str(winner.name + "#" + winner.discriminator)\
				for winner in winners)),
			inline = False
		)

		embed.set_image(url = self.image_url[self.last_match_details[3]])
		embed.set_thumbnail(url = self.ipl_logo)
		await ctx.send(embed = embed)

		await fetch_standings()

	@commands.command()
	async def standings(self, ctx):
		""" See current standings of Sattebaaz Championship
		"""
		await fetch_standings()

	@commands.command()
	async def score(self, ctx):
		""" Get live score of present IPL match
		"""
		if (self.config_data[0] >= 95):
			response_dog = requests.get(self.dog_api).json()[0]

			embed = discord.Embed(
				title = "Bruh...",
				color = 0xea1010			# Red
			)
			embed.add_field(
				name = "100/100 requests made for the day!",
				value = "Sorry! But I ain't Ambani bruh? Anyway here is a cute doggo ❤"
			)
			embed.set_image(url = response_dog["url"])
			await ctx.send(embed = embed)
			return
		
		else:
			self.config[0] += 1
			query = """UPDATE CONFIG
						SET RATE_LIMIT = RATE_LIMIT + 1"""
			
		response = requests.get(self.api_score, params = params_score)
		data = response.json()

		if (data["matchStarted"] == False):
			response_dog = requests.get(self.dog_api).json()[0]

			embed = discord.Embed(
				title = "Bruh...",
				color = 0xea1010			# Red
			)
			embed.add_field(
				name = "The match has not even started yet 🤦‍♂️",
				value = "Wait till the match starts? Anyway here is a cute doggo ❤"
			)
			embed.set_image(url = response_dog["url"])
			await ctx.send(embed = embed)
			return
		
		index_v = data["score"].find("v")
		if (data["score"][-1] != "*"):
			current_batting = data["team-1"]
		else:
			current_batting = data["team-2"]

		embed = discord.Embed(
			title = "Live Score",
			color = 0x25dbf4,					# Blue
		)
		embed.add_field(
			name = "Team A",
			value = data["score"][:index_v],
			inline = False
		)
		embed.add_field(
			name = "Team B",
			value = data["score"][index_v + 1:],
			inline = False
		)
		embed.set_image(url = self.image_url[current_batting])
		embed.set_thumbnail(url = self.ipl_logo)
		await ctx.send(embed = embed)
