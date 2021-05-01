import discord
from discord.ext import commands

import aiohttp
import json
import random
import logging


class Meme(commands.Cog):
	""" Get memes"""

	# Different func so that I could schedule it
	async def meme_code(self, endpoint = "dankmemes"):
		log = logging.getLogger("meme")
		dog_api = "https://api.thedogapi.com/v1/images/search"

		api = "https://meme-api.herokuapp.com/gimme"
		async with aiohttp.ClientSession() as session:
			async with session.get(api) as response:
				if response.status == 200:
					response = response.json()
					
				else:
					log.warning(f"Subreddit Requested: {endpoint}")
					log.error(f'Status Code: {response["code"]}')
					log.error(f'Error: {response["message"]}')

					async with aiohttp.ClientSession() as error_session:
						async with error_session.get(dog_api),json() as response:
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