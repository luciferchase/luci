import discord
from discord.ext import commands

import aiohttp
import asyncio
import os
import psycopg2
import random
import time


categories = [
	{
	  "id": 9,
	  "name": "General Knowledge"
	},
	{
	  "id": 10,
	  "name": "Entertainment: Books"
	},
	{
	  "id": 11,
	  "name": "Entertainment: Film"
	},
	{
	  "id": 12,
	  "name": "Entertainment: Music"
	},
	{
	  "id": 14,
	  "name": "Entertainment: Television"
	},
	{
	  "id": 15,
	  "name": "Entertainment: Video Games"
	},
	{
	  "id": 17,
	  "name": "Science & Nature"
	},
	{
	  "id": 18,
	  "name": "Science: Computers"
	},
	{
	  "id": 19,
	  "name": "Science: Mathematics"
	},
	{
	  "id": 20,
	  "name": "Mythology"
	},
	{
	  "id": 21,
	  "name": "Sports"
	},
	{
	  "id": 22,
	  "name": "Geography"
	},
	{
	  "id": 23,
	  "name": "History"
	},
	{
	  "id": 24,
	  "name": "Politics"
	},
	{
	  "id": 25,
	  "name": "Art"
	},
	{
	  "id": 26,
	  "name": "Celebrities"
	},
	{
	  "id": 27,
	  "name": "Animals"
	},
	{
	  "id": 29,
	  "name": "Entertainment: Comics"
	},
	{
	  "id": 31,
	  "name": "Entertainment: Japanese Anime & Manga"
	},
  ]


class Quiz(commands.Cog):
	"""Play a trivia quiz from a bunch of categories"""

	def __init__(self, bot):
		self.bot = bot
		self.categories = categories

		# Get emojis
		self.coolcry = self.bot.get_emoji(780445565476798475)
		self.smart = self.bot.get_emoji(839468976539172864)
		self.nacho = self.bot.get_emoji(839499460874862655)

		self.luciferchase = self.bot.get_user(707557256220115035)

		# Initialize a session
		self.session = aiohttp.ClientSession()

		# Connect with the database
		DATABASE_URL = os.environ["DATABASE_URL"]

		self.dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		self.cursor = self.dbcon.cursor()


	async def send_question(self, category_id, difficulty_level, token):
		# Fetch a question and send it as embed
		api = "https://opentdb.com/api.php"
		params = {
			"amount": 1,
			"category": category_id,
			"difficulty": difficulty_level,
			"type": "multiple",
			"token": token
		}

		# If random is selected, remove category from params
		if (category_id == 1):
			del params["category"]
		
		with self.session.get(api, params = params) as response:
			data = await response.json()

			# If there is an error while fetching questions
			if (data["response_code"] != 0):
				await ctx.send(f"Uh oh! I faced some error {self.coolcry}.")
				await ctx.send(f"Please run the command again or inform {self.luciferchase}")
				return

		question = data["question"]

		correct_answer = data["correct_answer"]
		options = data["incorrect_answers"]
		reactions = ["🇦", "🇧", "🇨", "🇩"]

		# Get a random index
		correct_index = random.randint(0, 3)

		# Insert the correct answer at the correct index
		options.insert(correct_index, correct_answer)

		# Make string for the embed
		description = ""
		for index in range(4):
			description = f"{reactions[index]}\t {option[index]}\n"

		# Send the embed
		embed = discord.Embed(title = question, description = description)
		return correct_index, correct_answer, embed
		
	@commands.command(aliases = ["trivia"])
	async def quiz(self, ctx):
		"""Play a trivia quiz from a bunch of categories"""

		# Get a session token first
		async with self.session.get("https://opentdb.com/api_token.php?command=request") as response:
			data = await response.json()

			if (data["response_code"] == 0):
				token = data["token"]
			else:
				await ctx.send(f"Uh oh! I faced some error {self.coolcry}.")
				await ctx.send(f"Please run the command again or inform {self.luciferchase}")

		# Let the player choose a category
		reactions = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", \
		"🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"]

		await ctx.send("You have 60 seconds to choose a category. Select random to get questions from all categories.")
		
		description = "🇦 Random\n"
		valid_reactions = {":regional_indicator_a": 1}
		
		for index in range(19):
			description += f'{reactions[index + 1]} {categories[index]["name"]}\n'

			# Add it to the dictionary
			valid_reactions[reactions[index + 1]] = categories[index]["id"]

		embed = discord.Embed(
			title = "Categories",
			description = description,
			color = 0x07f223
		)

		message = await ctx.send(embed = embed)

		# Add reactions
		for index in range(20):
			await message.add_reaction(reactions[index])

		category_chosen = False

		while not category_chosen:
			# Try for 60 seconds
			try:
				# Check if the user has chosen a category or not
				def check(payload: discord.RawReactionActionEvent):
					if (payload.user_id != self.bot.user.id and message.id == payload.message_id):
						return True

				payload: discord.RawReactionActionEvent = await self.bot.wait_for(
						"raw_reaction_add", timeout = 60, check = check
					)

				emoji = payload.emoji.name
				
				if (emoji in valid_reactions and payload.user_id == ctx.author.id):
					category_chosen = True
					category_id = valid_reactions[emoji]

					# Delete category list
					await message.delete()

			# Self abort the game after 30 seconds
			except asyncio.TimeoutError:
				category_chosen = True

				await message.edit(content = f"Timeout. Game aborted! {self.coolcry}", embed = None)
				return

		# Let the player choose difficulty level
		difficulty = {
			"🇦": {"difficulty_level": "easy", "points": 5}, 
			"🇧": {"difficulty_level": "medium", "points": 10},
			"🇨": {"difficulty_level": "hard", "points": 20}
		}

		description = ""
		for level in difficulty:
			description += f'{level} {difficulty[level]["difficulty_level"]} [{difficulty[level]["difficulty_level"]} points for each correct answer]\n'

		embed = discord.Embed(
			title = "Select Difficulty (Default is Medium)",
			description = description,
			color = 0x07f223
		)
		message = await ctx.send(embed = embed)

		for emoji in difficulty:
			message.add_reaction(emoji)

		difficulty_chosen = False

		while not difficulty_chosen:
			# Try for 30 seconds
			try:
				# Check if the user has chosen a category or not
				def check(payload: discord.RawReactionActionEvent):
					if (payload.user_id != self.bot.user.id and message.id == payload.message_id):
						return True

				payload: discord.RawReactionActionEvent = await self.bot.wait_for(
						"raw_reaction_add", timeout = 30, check = check
					)

				emoji = payload.emoji.name
				
				if (emoji in ["🇦", "🇧", "🇨"] and payload.user_id == ctx.author.id):
					difficulty_chosen = True
					difficulty_level = difficulty[emoji]["difficulty_level"]
					difficulty_points = difficulty[emoji]["points"]

					# Delete difficulty list
					await message.delete()

			# Self abort the game after 30 seconds
			except asyncio.TimeoutError:
				difficulty_chosen = True
				
				# Delete difficulty list
				await message.delete()

				# Default to medium difficulty
				difficulty_level = "medium"
				difficulty_points = 10

		# Start the game
		game_ended = False
		points = 0
		questions_attempted = 0

		reactions = ["🇦", "🇧", "🇨", "🇩", "❌"]

		while not game_ended and questions_attempted <= 50:
			# Fetch question first
			correct_index, correct_answer, message = await self.send_question(category_id, difficulty_level, token)
			for index in range(5):
				await message.add_reaction(reactions[index])

			# Try for 60 seconds
			try:
				# Check if the user has selected an option or not
				def check(payload: discord.RawReactionActionEvent):
					if (payload.user_id != self.bot.user.id and message.id == payload.message_id):
						return True

				payload: discord.RawReactionActionEvent = await self.bot.wait_for(
						"raw_reaction_add", timeout = 60, check = check
					)

				emoji = payload.emoji.name
				
				if (emoji in reactions and payload.user_id == ctx.author.id):
					if (emoji == "❌"):
						game_ended = True

						embed = discord.Embed(
							title = f"{ctx.author.name} Thank you for playing! {self.nacho}",
							color = 0x07f223
						)
						await message.edit(embed = embed)
						break
					
					if (reactions.index(emoji) == correct_index):
						points += difficulty_points

						await ctx.send(content = f"{self.smart} Correct Answer!", delete_after = 5)
					else:
						await ctx.send(content = f"{self.coolcry} Incorrect Answer!", delete_after = 5)
						await ctx.send(content = f"The correct answer is {correct_answer}", delete_after = 5)

					questions_attempted += 1

			# Self abort the game after 60 seconds
			except asyncio.TimeoutError:
				difficulty_chosen = True
				
				# Default to medium difficulty
				difficulty_level = "medium"

		await ctx.send(points)