import discord
from discord.ext import commands

import aiohttp
import asyncio
import os
import psycopg2
import time


class Quiz(commands.Cog):
	"""Play a trivia quiz from a bunch of categories"""

	def __init__(self, bot):
		self.bot = bot

		# Initialize a session
		self.session = aiohttp.ClientSession()

		# Connect with the database
		DATABASE_URL = os.environ["DATABASE_URL"]

		self.dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		self.cursor = self.dbcon.cursor()

	@commands.command(aliases = ["trivia"])
	async def quiz(self, ctx):
		"""Play a trivia quiz from a bunch of categories"""

		# Get a session token first
		async with self.session.get("https://opentdb.com/api_token.php?command=request") as response:
			data = await response.json()

			if (data["response_code"] == 0):
				token = data["token"]
			else:
				coolcry = self.bot.get_emoji(780445565476798475)
				luciferchase = self.bot.get_user(707557256220115035)

				await ctx.send(f"Uh oh! I faced some error {coolcry}. Please run the command again or inform {luciferchase}")

		# Get categories
		async with self.session.get("https://opentdb.com/api_category.php") as response:
			data = await response.json()

			categories = data["trivia_categories"]
		
		# Let the player choose a category
		reactions = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "🇯", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", \
		"🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"]

		await ctx.send("You have 30 seconds to choose a category. Select random to get questions from all categories.")
		
		description = "🇦: Random"
		valid_reactions = {":regional_indicator_a": 1}
		
		for index in range(20):
			description += f'{reactions[index + 1]} {categories[index]["name"]}\n'

			# Add it to the dictionary
			valid_reactions[f":regional_indicator_{chr(98 + index)}"] = categories[index]["id"]

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

				if (emoji in valid_reactions and payload.user.id == ctx.author.id):
					category_chosen = True
					category = valid_reactions[emoji]

					# Debugging
					await ctx.send(category)

					# Delete category list
					await message.delete()

			# Self abort the game after 30 seconds
			except asyncio.TimeoutError:
				category_chosen = True

				await message.edit(f"Timeout. Game aborted! {coolcry}")