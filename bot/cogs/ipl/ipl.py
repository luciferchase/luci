import discord
from discord.ext import commands

from datetime import date, timedelta
import os
import psycopg2
import requests

class IPL(commands.Cog):
	"""Get info about today's as well as last match in IPL. See current score and play Sattebaaz Championship"""

	def __init__(self, bot):
		self.bot = bot

		self.api_matches = "https://cricapi.com/api/matches?"
		self.api_score = "https://cricapi.com/api/cricketScore?"
		self.apikey = os.getenv("CRIC_API_KEY")

		# Initialize Connection to database
		DATABASE_URL = os.environ['DATABASE_URL']
		self.dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		self.cursor = self.dbcon.cursor()

		# Links for image url of all the teams and the ipl logo
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

	# Update details of last match and upcoming match
	def fetch_matches(self):
		# Fetch matches from website
		params = {"apikey": self.apikey}
		response = requests.get(url = self.api_matches, params = params).json()

		# Details about the last match
		last_match = []

		# Details about the todays match
		next_match = []

		for match in response["matches"]:
			# If last match id is similar to IPL matches' ID and date was yesterday 
			# then add the match to last match list

			if (str(match["unique_id"])[:-2] == "12540"\
			 and match["date"][:10] == str(date.today() - timedelta(days = 1))):
				# date.today() - timedelta(days = 1) yields yesterday's date

				last_match.append(match)

			# If date is todays date
			if (str(match["unique_id"])[:-2] == "12540"\
			 and match["date"][:10] == str(date.today())):
				next_match.append(match)
			
		# On normal days, there should be only one last match and second match should be False
		last_match_details = last_match[0]
		last_match_details_2 = False

		# However when there were two matches yesterday, add it to last match details 2
		if (len(last_match) > 1):
			last_match_details_2 = last_match[1]

		# Similarly make details of next match also
		next_match_details = next_match[0]
		next_match_details_2 = False

		if (len(next_match) > 1):
			next_match_details_2 = next_match[1]

		# Return the details
		return (last_match_details, last_match_details_2, next_match_details, next_match_details_2)

	@commands.command()
	async def ipl(self, ctx):
		"""Get info about last match and upcoming matches"""

		# Fetch details first
		last_match_details, last_match_details_2, \
		next_match_details, next_match_details_2 = self.fetch_matches()

		embed = discord.Embed(
			color = 0x25dbf4,					# Blue
			title = "Matches"
		)
		embed.add_field(
			name = "Next Match", 
			value = f'{next_match_details["team-1"]} \nvs \
			\n{next_match_details["team-2"]}',
			inline = False
		)

		# If there is a second match on that day
		if (next_match_details_2 != False):
			embed.add_field(
				name = "Match 2", 
				value = f'{next_match_details_2["team-1"]} \nvs \
				\n{next_match_details_2["team-2"]}',
				inline = False
			)

		embed.add_field(
			name = "Last Match",
			value = f'{last_match_details["team-1"]} \nvs \n{last_match_details["team-2"]}',
			inline = True
		)
		embed.add_field(
			name = "Winner",
			value = f'{last_match_details["winner_team"]}',
			inline = True
		)
		image_url = self.image_url[last_match_details["winner_team"]]

		# If there was another match yesterday
		if (last_match_details_2 != False):
			embed.add_field(
				name = "Match 2", 
				value = f'{last_match_details_2["team-1"]} \nvs \
				\n{last_match_details_2["team-2"]}',
				inline = False
			)
			embed.add_field(
				name = "Winner",
				value = f'{last_match_details_2["winner_team"]}',
				inline = True
			)
			# Update the image to show
			image_url = self.image_url[last_match_details_2["winner_team"]]

		embed.set_image(url = image_url)
		embed.set_thumbnail(url = self.ipl_logo)
		await ctx.send(embed = embed)

	def fetch_score(self, match_details):
		# Set up params
		params = {"apikey": self.apikey, "unique_id": match_details["unique_id"]}
		response = requests.get(url = self.api_score, params = params)
		data = response.json()

		# If the First Match too hasn't started
		if (data["matchStarted"] == False):

			# Send a cute dog image/gif
			dog_api = "https://api.thedogapi.com/v1/images/search"
			response_dog = requests.get(dog_api).json()[0]

			embed = discord.Embed(
				title = "Bruh...",
				color = 0xea1010			# Red
			)
			embed.add_field(
				name = "The match has not even started yet 🤦‍♂️",
				value = "Wait till the match starts? Anyway here is a cute doggo ❤"
			)
			embed.set_image(url = response_dog["url"])
			return embed

		# Differentiate between the first team and the second team		
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
		return embed

	@commands.command()
	async def score(self, ctx):
		"""See live score"""
		await ctx.trigger_typing()

		*_, next_match_details, next_match_details_2 = self.fetch_matches()

		# Check if there is second match
		if (next_match_details_2 != False):
			# If the second match has indeed started
			if (next_match_details_2["matchStarted"] != False):
				match_details = next_match_details_2

		# Else in all other cases go with the first match of the day
		else:
			match_details = next_match_details

		embed = self.fetch_score(match_details)
		await ctx.send(embed = embed)

	async def fetch_standings(self):
		# Fetch standings from the database

		self.cursor.execute("SELECT * FROM STANDINGS")
		data = self.cursor.fetchall()

		current_standings = {}

		for user in data:
			# user = (user, points)
			# Fetch username
			user_info = self.bot.get_user(user[0])
			username = user_info.name

			# Make a dictionary of the form
			# {username: points}
			current_standings[username] = user[1]

		# Sort the the standings according to their value
		current_standings = dict(sorted(current_standings.items(), key = lambda item: item[1], reverse = True))
		leaderboard = [user for user in current_standings]

		embed = discord.Embed(
			title = "Current Standings"
		)
		embed.set_thumbnail(url = self.ipl_logo)

		# Add fields to the embed
		for index in range(len(leaderboard)):
			if (index == 0):
				embed.add_field(
					name = f":first_place: {leaderboard[index]}",
					value = f"Points: {current_standings[leaderboard[index]]}",
					inline = False
				)
			elif (index == 1):
				embed.add_field(
					name = f":second_place: {leaderboard[index]}",
					value = f"Points: {current_standings[leaderboard[index]]}",
					inline = False
				)
			elif (index == 2):
				embed.add_field(
					name = f":third_place: {leaderboard[index]}",
					value = f"Points: {current_standings[leaderboard[index]]}",
					inline = False
				)
			else:
				embed.add_field(
					name = f"➡️ {leaderboard[index]}",
					value = f"Points: {current_standings[leaderboard[index]]}",
					inline = False
				)
		return embed

	@commands.command()
	async def standings(self, ctx):
		"""Get current standings of Sattebaaz Championship"""

		embed = await self.fetch_standings()
		await ctx.send(embed = embed)

	# Following are all owner only command
	async def predict_code(self, match_details):
		# Set Channel
		channel = self.bot.get_channel(756701639544668160)

		embed = discord.Embed(
			color = 0x19f0e2,						# Cyan
			title = "Sattebaaz Championship",
		)
		embed.add_field(
			name = "Who do you think will win today's match?",
			value = f':regional_indicator_a: {match_details["team-1"]}\n\
			:regional_indicator_b: {match_details["team-2"]}'
		)
		embed.set_thumbnail(url = self.ipl_logo)

		last_embed = await channel.send(embed = embed)
		await last_embed.add_reaction("🇦")
		await last_embed.add_reaction("🇧")

		return (last_embed.id)

	@commands.is_owner()
	@commands.command(hidden = True)
	async def predict(self, ctx):
		*_, next_match_details, next_match_details_2 = self.fetch_matches()

		embed_id = await self.predict_code(next_match_details)

		# Update database
		self.cursor.execute("DELETE FROM predict")
		query = """INSERT INTO predict VALUES
				({})""".format(embed_id)
		self.cursor.execute(query)
		self.dbcon.commit()

		# If there is a second match on that day
		if (next_match_details_2 != False):
			embed_id = await self.predict_code(next_match_details_2)

			# Update database
			query = """INSERT INTO predict VALUES
					({})""".format(embed_id)
			self.cursor.execute(query)
			self.dbcon.commit()

	async def update_points(self, match_details, embed_id):
		# Get members details
		self.cursor.execute("SELECT * FROM standings")
		users = self.cursor.fetchall()

		# Get user ids of all members who has selected each team
		channel = self.bot.get_channel(756701639544668160)
		last_embed = await channel.fetch_message(embed_id)
		team_1 = []
		team_2 = []
		for reaction in last_embed.reactions:
			async for user in reaction.users():
				if (reaction.emoji == "🇦" and not user.bot):
					team_1.append(user.id)
				elif (reaction.emoji == "🇧" and not user.bot):
					team_2.append(user.id)

		# Get winners
		if (match_details["winner_team"] == match_details["team-1"]):
			winners = team_1
		else:
			winners = team_2

		# Update points
		for user in users:
			# First convert tuple into list
			user = list(user)
			if (user[0] in winners):
				user[1] += 10

		# Update database
		self.cursor.execute("DELETE FROM standings")
		self.dbcon.commit()

		for user in users:
			self.cursor.execute("INSERT INTO standings VALUES {}".format(tuple(user)))
			self.dbcon.commit()

		return winners

	async def show_points(self):
		# Get last match's details
		last_match_details, last_match_details_2, *_ = self.fetch_matches()

		# Get last embed id
		self.cursor.execute("SELECT * FROM predict")
		data = self.cursor.fetchall()
		embed_id = data[0][0]

		winners = await self.update_points(last_match_details, embed_id)

		# If there was another match yesterday
		if (last_match_details_2 != False):
			embed_id = data[1][0]
			second_winners = await self.update_points(last_match_details_2, embed_id)

		embed = discord.Embed(
			color = 0x07f223,						# Green
			title = "Sattebaaz Championship",
		)
		embed.add_field(
			name = "Last match was won by ...",
			value = last_match_details["winner_team"],
			inline = True
		)
		embed.add_field(
			name = "Winning sattebaaz",
			value = "`{}`".format("\n".join(str(winner.name + "#" + winner.discriminator)\
				for winner in winners)),
			inline = False
		)

		# Add another field if there was another match yesterday
		if (last_match_details_2 != False):
			embed.add_field(
				name = "Second match was won by ...",
				value = last_match_details_2["winner_team"],
				inline = True
			)
			embed.add_field(
				name = "Winning sattebaaz",
				value = "`{}`".format("\n".join(str(winner.name + "#" + winner.discriminator)\
					for winner in second_winners)),
				inline = False
			)

		embed.set_image(url = self.image_url[self.last_match_details["winner_team"]])
		embed.set_thumbnail(url = self.ipl_logo)
		return embed

	@commands.is_owner()
	@commands.command(hidden = True)
	async def points(self, ctx):
		"""Update points and show winners of last prediction(s)"""
		embed = await self.show_points()
		await ctx.send(embed = embed)
		
	@commands.is_owner()
	@commands.command(hidden = True)
	async def database(self, ctx):
		query = """CREATE TABLE IF NOT EXISTS predict
				(embed_id 	BIGINT	NOT NULL)"""
		self.cursor.execute(query)
		self.dbcon.commit()

		query = """CREATE TABLE IF NOT EXISTS standings(
				user_id		BIGINT	NOT NULL,
				points		INT 	NOT NULL)"""
		self.cursor.execute(query)
		self.dbcon.commit()
		await ctx.send("All tables created successfully")