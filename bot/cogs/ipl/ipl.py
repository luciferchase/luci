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

	async def fetch_score(self, match_details):
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

		last_match_details, last_match_details_2, \
		next_match_details, next_match_details_2 = self.fetch_score()

		# Check if there is second match
		if (next_match_details_2 != False):
			# If the second match has indeed started
			if (next_match_details_2["matchStarted"] != False):
				match_details = next_match_details_2

		# Else in all other cases go with the first match of the day
		else:
			match_details = next_match_details

		embed = await self.fetch_score(match_details)
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
		return embed

	@commands.command()
	async def standings(self, ctx):
		"""Get current standings of Sattebaaz Championship"""

		embed = await self.fetch_standings()
		await ctx.send(embed = embed)

	# Following are all owner only command
