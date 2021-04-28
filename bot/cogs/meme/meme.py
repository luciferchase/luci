import discord
from discord.ext import commands

import requests
import json
import random
import logging


class Meme(commands.Cog):
	""" Get memes.
	"""
	
	def __init__(self):
		self.log = logging.getLogger("red.cogsbylucifer.photo")
		self.dog_api = "https://api.thedogapi.com/v1/images/search"
		self.ctx = ctx
	
	@commands.command()
	async def meme(self, ctx = self.ctx, endpoint = ""):
		""" Get a meme from reddit. 
			To Get a meme from a specific subreddit, append its name after the command
			For eg. `luci meme wholesomememes`
		"""
		api = "https://meme-api.herokuapp.com/gimme"
		if (endpoint != ""):
			response = requests.get(api + "/" + endpoint).json()
		else:
			response = requests.get(api + "/" + "dankmemes").json()

		if ("code" in response):
			self.log.info(f"Subreddit Requested: {endpoint}")
			self.log.error(f'Status Code: {response["code"]}')
			self.log.error(f'Error: {response["message"]}')

			response_dog = requests.get(self.dog_api).json()[0]

			embed = discord.Embed(
				title = "Bruh...",
				color = 0xea1010						# Red
			)
			embed.add_field(
				name = response["message"],
				value = "Try again maybe? Anyway here is a cute doggo ❤"
			)
			embed.set_image(url = response_dog["url"])
			await ctx.send(embed = embed)
			return
		
		elif (response["nsfw"]):
			response = requests.get(self.api)
		
		embed = discord.Embed(
			color = 0x06f9f5,							# Blue-ish
			title = response["title"],
			url = response["postLink"]
		)
		embed.set_image(url = response["url"])
		embed.set_footer(text = f'👍 {response["ups"]}')
		await ctx.send(embed = embed)