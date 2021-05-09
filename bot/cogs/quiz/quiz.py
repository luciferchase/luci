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

		# Initialize a session
		self.session = aiohttp.ClientSession()

		# Connect with the database
		DATABASE_URL = os.environ["DATABASE_URL"]

		self.dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		self.cursor = self.dbcon.cursor()

		# Create table if not exists
		query = """CREATE TABLE IF NOT EXISTS quiz(
				user_id					BIGINT		NOT NULL	PRIMARY KEY,
				points					INT 		NOT NULL,
				questions_attempted		INT 		NOT NULL,
				questions_correct		INT 		NOT NULL,
				guild_id				BIGINT		NOT NULL)"""
		self.cursor.execute(query)
		self.dbcon.commit()


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
		
		async with self.session.get(api, params = params) as response:
			data = await response.json()

		question = data["results"][0]["question"]

		correct_answer = data["results"][0]["correct_answer"]
		options = data["results"][0]["incorrect_answers"]
		reactions = ["🇦", "🇧", "🇨", "🇩"]

		# Get a random index
		correct_index = random.randint(0, 3)

		# Insert the correct answer at the correct index
		options.insert(correct_index, correct_answer)

		# Make string for the embed
		description = ""
		for index in range(4):
			description += f"{reactions[index]} {options[index]}\n"

		# Send the embed
		embed = discord.Embed(title = question, description = description, color = 0x00FFFFF)
		return correct_index, correct_answer, embed
		
	@commands.command(aliases = ["trivia"])
	async def quiz(self, ctx):
		"""Play a trivia quiz from a bunch of categories"""

		# Get emojis
		coolcry = self.bot.get_emoji(780445565476798475)
		smart = self.bot.get_emoji(839468976539172864)
		nacho = self.bot.get_emoji(839499460874862655)

		luciferchase = self.bot.get_user(707557256220115035)

		# Get a session token first
		async with self.session.get("https://opentdb.com/api_token.php?command=request") as response:
			data = await response.json()

			if (data["response_code"] == 0):
				token = data["token"]
			else:
				await ctx.send(f"Uh oh! I faced some error {coolcry}.")
				await ctx.send(f"Please run the command again or inform {luciferchase.mention}")

		# Let the player choose a category
		reactions = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", \
		"🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"]

		await ctx.send("You have 60 seconds to choose a category.", delete_after = 10)
		await ctx.send("Select random to get questions from all categories.", delete_after = 10)
		
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

				await message.edit(content = f"Timeout. Game aborted! {coolcry}", embed = None)
				return

		# Let the player choose difficulty level
		difficulty = {
			"🇦": {"difficulty_level": "easy", "points": 5}, 
			"🇧": {"difficulty_level": "medium", "points": 10},
			"🇨": {"difficulty_level": "hard", "points": 20}
		}

		description = ""
		for level in difficulty:
			description += f'{level} {difficulty[level]["difficulty_level"].title()} \
			[{difficulty[level]["points"]} points for each correct answer]\n'

		embed = discord.Embed(
			title = "Select Difficulty (Default is Medium)",
			description = description,
			color = 0x07f223
		)
		message = await ctx.send(embed = embed)

		for emoji in difficulty:
			await message.add_reaction(emoji)

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
		questions_correct = 0

		reactions = ["🇦", "🇧", "🇨", "🇩", "❌"]

		embed = discord.Embed(
			title = "Controls",
			description = f"You have 60 seconds for each question.\nYou will get {difficulty_points} for each question.\nYou can click on ❌ anytime to close the game.\nEnjoy {nacho}",
			color = 0x07f223
		)
		message = await ctx.send(embed = embed)
		footnote = await ctx.send(f"{nacho} Best of luck")

		while not game_ended and questions_attempted <= 50:
			# Fetch question first
			correct_index, correct_answer, embed = await self.send_question(category_id, difficulty_level, token)
			await message.edit(embed = embed)

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
							title = f"{ctx.author.name} Thank you for playing! {nacho}",
							color = 0x07f223
						)
						await message.edit(embed = embed)
						await message.clear_reactions()
						await footnote.delete()
						
						break
					
					if (reactions.index(emoji) == correct_index):
						points += difficulty_points
						questions_correct += 1
						
						await footnote.edit(content = f"{smart} Correct Answer!")

					else:
						await footnote.edit(content = f"{coolcry} Incorrect Answer!\nThe correct answer is {correct_answer}.")

					await message.remove_reaction(payload.emoji, discord.Object(id = payload.user_id))
					questions_attempted += 1

			# Self abort the game after 60 seconds
			except asyncio.TimeoutError:
					game_ended = True

					await message.delete()
					await footnote.edit(f"{coolcry} Game aborted automatically!")
					
					break

		# Update database
		query = f"""UPDATE quiz
				SET points = points + {points}
				WHERE user_id = {ctx.author.id}"""
		self.cursor.execute(query)
		self.dbcon.commit()

		# Send final embed
		embed = discord.Embed(
			title = "Total Points",
			description = points,
			color = 0x07f223
		)
		embed.add_field(name = "Questions Played:", value = questions_attempted, inline = True)
		embed.add_field(name = "Questions Correct:", value = questions_correct, inline = True)
		embed.add_field(
			name = "Category:", 
			value = [category for category in self.categories if category["id"] == category_id][0]["name"],
			inline = False
		)