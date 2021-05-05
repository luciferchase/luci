import discord
from discord.ext import commands

import aiohttp
import requests
import json
import random
import logging


class Meme(commands.Cog):
	""" Get memes"""
	def __init__(self):
		self.dog_api = "https://api.thedogapi.com/v1/images/search"
		self.meme_api = "https://meme-api.herokuapp.com/gimme/"

		# Make a aiohttp session
		self.session = aiohttp.ClientSession()

	@commands.command()
	async def meme(self, ctx, endpoint = "dankmemes"):
		"""Get memes from reddit. To get memes from a specific subreddit, add its name at the end
		For eg. `luci meme` to get a random meme
				`luci meme wholesomememes` to get a meme from r/wholesomememes"""

		log = logging.getLogger("meme")

		async with self.session.get(self.meme_api + endpoint) as response:
			data = await response.json()
			
			# If the query was successfull
			if (response.status == 200):
				embed = discord.Embed(
					color = 0x06f9f5,							# Blue-ish
					title = data["title"],
					url = data["postLink"]
				)
				embed.set_image(url = data["url"])
				embed.set_footer(text = f'👍 {data["ups"]}')
				await ctx.send(embed = embed)

			else:
				status_code = data["code"]
				status_message = data["message"]

		# Else send a random dog photo
		async with self.session.get(self.dog_api) as response:

			log.warning(f"Subreddit Requested: {endpoint}")
			log.error(f'Status Code: {status_code}')
			log.error(f'Error: {status_message}')

			data = await response.json()[0]

			embed = discord.Embed(
				title = "Bruh...",
				color = 0xea1010						# Red
			)
			embed.add_field(
				name = status_message,
				value = "Try again maybe? Anyway here is a cute doggo ❤"
			)
			embed.set_image(url = data["url"])
			await ctx.send(embed = embed)

	@commands.command()
	async def memespam(self, ctx, endpoint = "dankmemes", count = 5):
		"""Spam number of memes so that you don't have to type `luci meme` everytime
		Usage: `luci memespam [subreddit[optional]] [number of memes to spam[Max = 50, Default = 5]]"""
		if (count > 50):
			await ctx.send("Bruh! Get a life bro. Can't request more than 50 memes at a time 🤦‍♂️")

		async with self.session.get(self.meme_api + str(count)) as response:
			# If the query was successfull
			if (response.status == 200):
				data = await response.json()["memes"]

				for meme in data:
					embed = discord.Embed(
						color = 0x06f9f5,							# Blue-ish
						title = data["title"],
						url = data["postLink"]
					)
					embed.set_image(url = data["url"])
					embed.set_footer(text = f'👍 {data["ups"]}')
					await ctx.send(embed = embed)

				else:
					status_code = data["code"]
					status_message = data["message"]

			# Else send a random dog photo
			async with self.session.get(self.dog_api) as response:
				log.error(f'Status Code: {status_code}')
				log.error(f'Error: {status_message}')

				data = await response.json()[0]

				embed = discord.Embed(
					title = "Bruh...",
					color = 0xea1010						# Red
				)
				embed.add_field(
					name = status_message,
					value = "Try again maybe? Anyway here is a cute doggo ❤"
				)
				embed.set_image(url = data["url"])
				await ctx.send(embed = embed)
