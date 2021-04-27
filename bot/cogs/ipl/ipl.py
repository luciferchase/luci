import discord
from discord.ext import commands

import os
import requests
import json
from datetime import date, datetime
import calendar

config = {
	"rate_limit": 1,
	"matches": {
		"last_requested": "2021-04-27",
		"last_match_id": 1254078
	},
	"predict": {
		"embed_id": 836433440421052417,
		"channel_id": 756701639544668160,
		"users": {
			"707557256220115035": 20,
			"650661454000947210": 20,
			"707935222267904070": 0,
			"708149141909274696": 10,
			"713963160641601548": 30,
			"735347909163352084": 10,
			"708578251320066068": 0
		}
	}
}

image_url = {
	"IPL Logo": "https://img.etimg.com/thumb/width-1200,height-900,imgsize-121113,resizemode-1,msid-81376248/ipl-2021-from-april-9-six-venues-no-home-games-no-spectators.jpg",
	"Kolkata Knight Riders": "https://hdsportsnews.com/wp-content/uploads/2020/01/kolkata-knight-riders-kkr-2020-team-squad-players-live-score-time-table-point-table-schedule-auction-match-fixture-venue-highlight-1280x720.jpg",			
	"Rajasthan Royals": "https://cdn5.newsnationtv.com/images/2021/02/22/royal-rajasthan-logo-70.jpg",			
	"Royal Challengers Bangalore": "https://english.sakshi.com/sites/default/files/article_images/2020/11/8/RCB-Logo_571_855-1604821493.jpg",			
	"Mumbai Indians": "https://static.india.com/wp-content/uploads/2017/03/mumbai.jpg?impolicy=Medium_Resize&w=1200&h=800",			
	"Punjab Kings": "https://awaj.in/wp-content/uploads/2021/03/20210317_222651.jpg",			
	"Sunrisers Hyderabad": "https://2.bp.blogspot.com/-6cAZUQMFCqc/WwKFUZrPPmI/AAAAAAAACcM/TryzryihpEkoOMd6htpE8LjIH1r02FWSgCLcBGAs/s1600/SRH.jpg",			
	"Chennai Super Kings": "https://i.pinimg.com/originals/85/52/f8/8552f811e95b998d9505c43a9828c6d6.jpg",			
	"Delhi Capitals": "https://d3pc1xvrcw35tl.cloudfront.net/ln/images/686x514/teamsinnerintrodc534x432-resize-534x432-a7542dd51f-d979030f10e79596_202009106828.jpeg"
}

response = requests.get(url = "https://cricapi.com/api/matches?apikey=" + os.getenv("CRIC_API_KEY"))
matches = json.dumps(response.json(), indent = 2)


class IPL(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.dog_api = "https://api.thedogapi.com/v1/images/search"

		self.config = config
		self.matches = matches
		self.config["rate_limit"] += 1

		self.api = "https://cricapi.com/api/"
		self.api_key = os.getenv("CRIC_API_KEY")
		self.api_endpoint = {
			"matches": "matches",
			"score": "cricketScore"
		}
		self.params_match = {
			"apikey": self.api_key,
		}
		self.params_score = {
			"apikey": self.api_key,
			"unique_id": self.config["matches"]["last_match_id"] + 1
		}

		# Increment last match id for sunday double matches

		if (calendar.day_name[date.today().weekday()] == "Sunday" \
			and str(datetime.now().time())[:5] >= "19:30"):
			self.params_score["unique_id"] += 1
			self.config["matches"]["last_match_id"] += 1

		# If last requested is yesterday

		if (str(date.today()) > self.config["matches"]["last_requested"]):
			self.config["matches"]["last_requested"] = str(date.today())
			self.config["matches"]["last_match_id"] += 1
			self.config["rate_limit"] = 1

			response = requests.get(
				url = self.api + self.api_endpoint["matches"] + "?", 
				params = self.params_match
			)
			self.matches = json.dumps(response.json(), indent = 2)

		self.last_match_id = self.config["matches"]["last_match_id"]

		for match in self.matches["matches"]:
			if (match["unique_id"] == self.last_match_id):
				self.last_match_details = match
			elif (match["unique_id"] == self.last_match_id + 1):
				self.upcoming_match_details = match
			elif (match["unique_id"] == self.last_match_id + 2):
				self.upcoming_match_details_2 = match

		self.image_url = image_url
		self.ipl_logo = image_url["IPL Logo"]

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
			value = f'{self.upcoming_match_details["team-1"]} \nvs \
			\n{self.upcoming_match_details["team-2"]}',
			inline = False
		)
		if (calendar.day_name[date.today().weekday()] == "Sunday"):
			embed.add_field(
			name = "Match 2", 
			value = f'{self.upcoming_match_details_2["team-1"]} \nvs \
			\n{self.upcoming_match_details_2["team-2"]}',
			inline = False
			)
		embed.add_field(
			name = "Last Match",
			value = f'{self.last_match_details["team-1"]} \nvs \n{self.last_match_details["team-2"]}',
			inline = True
		)
		embed.add_field(
			name = "Winner",
			value = f'{self.last_match_details["winner_team"]}',
			inline = True
		)
		embed.set_image(url = self.image_url[self.last_match_details["winner_team"]])
		embed.set_thumbnail(url = self.ipl_logo)
		await ctx.send(embed = embed)

	async def update_standings(self, ctx, match = 1):

		if (match == 2):
			self.upcoming_match_details = self.upcoming_match_details_2

			channel = self.bot.get_channel(self.config["predict"]["channel_id"])
			last_embed = await channel.fetch_message(self.config["predict"]["embed_id"])
			emoji_a = []
			emoji_b = []
			winners = []
			for reaction in last_embed.reactions:
				async for user in reaction.users():
					if (reaction.emoji == "🇦" and user.id != 829537216224165888):
						emoji_a.append(str(user.id))
					elif (reaction.emoji == "🇧" and user.id != 829537216224165888):
						emoji_b.append(str(user.id))

		if (self.last_match_details["winner_team"] == self.last_match_details["team-1"]):
			for user in emoji_a:
				self.config["predict"]["users"][user] += 10
				username = await self.bot.fetch_user(user)
				winners.append(username)
		else:
			for user in emoji_b:
				self.config["predict"]["users"][user] += 10
				username = await self.bot.fetch_user(user)
				winners.append(username)

		return winners

	@commands.bot_has_permissions(embed_links = True)
	@commands.is_owner()
	@commands.command(hidden = True)
	async def predict(self, ctx, match = 1):
		""" Poll for today's match
		"""
		allowed_mentions = discord.AllowedMentions(everyone = True)
		await ctx.send(content = "@everyone", allowed_mentions = allowed_mentions)

		winners = update_standings(ctx, match)
		
		embed = discord.Embed(
			color = 0x19f0e2,						# Cyan
			title = "Sattebaaz Championship",
		)
		embed.add_field(
			name = "Who do you think will win today's match?",
			value = f':regional_indicator_a: {self.upcoming_match_details["team-1"]}\n\
			:regional_indicator_b: {self.upcoming_match_details["team-2"]}'
		)
		embed.set_thumbnail(url = self.ipl_logo)

		last_embed = await ctx.send(embed = embed)
		await last_embed.add_reaction("🇦")
		await last_embed.add_reaction("🇧")
		self.config["predict"]["embed_id"] = last_embed.id
		self.config["predict"]["channel_id"] = last_embed.channel.id
		
	@commands.bot_has_permissions(embed_links = True)
	@commands.is_owner()
	@commands.command(hidden = True)
	async def points(self, ctx):
		""" Update Standings for Sattebaaz Championship
		"""
		winners = update_standings(ctx)

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

		embed.set_image(url = self.image_url[self.last_match_details["winner_team"]])
		embed.set_thumbnail(url = self.ipl_logo)
		await ctx.send(embed = embed)

		points = {}
		for user in self.config["predict"]["users"]:
			username = await self.bot.fetch_user(user)
			points[username] = self.config["predict"]["users"][user]

		embed_string_name = ""
		embed_string_points = ""
		for user in points:
			embed_string_name += f"\n{user}\n"
			embed_string_points += f"\n : \t {points[user]}\n"

		embed = discord.Embed(
			color = 0x07f223,						# Green
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

	@commands.command()
	async def standings(self, ctx):
		""" See current standings of Sattebaaz Championship
		"""
		points = {}
		for user in self.config["predict"]["users"]:
			username = await self.bot.fetch_user(user)
			points[username] = self.config["predict"]["users"][user]

		embed_string_name = ""
		embed_string_points = ""
		for user in points:
			embed_string_name += f"\n{user}\n"
			embed_string_points += f"\n : \t {points[user]}\n"

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

	@commands.command()
	async def score(self, ctx):
		""" Get live score of present IPL match
		"""
		if (self.config["rate_limit"] >= 95):

			embed = discord.Embed(
				title = "Bruh...",
				color = 0xea1010			# Red
			)
			embed.add_field(
				name = "100/100 requests made for the day!",
				value = "Sorry! But I ain't Ambani bruh? Anyway here is a cute doggo ❤"
			)
			embed.set_image(url = response["url"])
			await ctx.send(embed = embed)
			return
		
		else:
			self.config["rate_limit"] += 1
			
		response = requests.get(
			url = self.api + self.api_endpoint["score"] + "?", 
			params = self.params_score
		)
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