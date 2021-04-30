import discord
from discord.ext import commands

import requests
import json
import random
import logging


class Meme(commands.Cog):
	""" Get memes"""

	# Different func so that I could schedule it
	async def meme_code(self, endpoint = ""):
		log = logging.getLogger("meme")
		dog_api = "https://api.thedogapi.com/v1/images/search"

		api = "https://meme-api.herokuapp.com/gimme"
		if (endpoint != ""):
			response = requests.get(api + "/" + endpoint).json()
		else:
			response = requests.get(api + "/" + "dankmemes").json()

		if ("code" in response):
			log.warning(f"Subreddit Requested: {endpoint}")
			log.error(f'Status Code: {response["code"]}')
			log.error(f'Error: {response["message"]}')

			response_dog = requests.get(dog_api).json()[0]

			embed = discord.Embed(
				title = "Bruh...",
				color = 0xea1010						# Red
			)
			embed.add_field(
				name = response["message"],
				value = "Try again maybe? Anyway here is a cute doggo ❤"
			)
			embed.set_image(url = response_dog["url"])
			return embed
		
		elif (response["nsfw"]):
			response = requests.get(self.api)
		
		embed = discord.Embed(
			color = 0x06f9f5,							# Blue-ish
			title = response["title"],
			url = response["postLink"]
		)
		embed.set_image(url = response["url"])
		embed.set_footer(text = f'👍 {response["ups"]}')
		return embed

	@commands.command()
	async def meme(self, ctx, endpoint = ""):
		""" Get a meme from reddit. 
			To Get a meme from a specific subreddit, append its name after the command
			For eg. `luci meme wholesomememes`
		"""
		embed = await self.meme_code(endpoint)
		await ctx.send(embed = embed)