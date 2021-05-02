import discord
from discord.ext import commands

from datetime import date, datetime
import json
import logging
import os
import requests


class Photo(commands.Cog):
	"""Various fun photo commands"""

	def __init__(self):
		self.log = logging.getLogger("red.cogsbylucifer.photo")

		self.unsplash_api = "https://api.unsplash.com"
		self.bing_api = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-IN"

		self.dog_api = "https://api.thedogapi.com/v1/images/search"
		self.cat_api = "https://api.thecatapi.com/v1/images/search"
		self.fox_api = "https://randomfox.ca/floof/"
		self.panda_api = "https://some-random-api.ml/img/panda"
		self.red_panda_api = "https://some-random-api.ml/img/red_panda"
		self.birb_api = "https://some-random-api.ml/img/birb"
		self.koala_api = "https://some-random-api.ml/img/koala"

		self.unsplash_client_id = os.getenv("UNSPLASH_API_KEY")
	
	@commands.command(aliases = ["photu", "image", "img"])
	async def photo(self, ctx, *query):
		""" Get a photo from Unsplash. 
			For eg. `luci photo messi`
			Default to a random photo
		"""
		endpoint_list = {
			"search": "/search/photos",
			"random": "/photos/random"
		}
		params = {
			"client_id": self.unsplash_client_id,
			"query": f"{' '.join(query)}",
			"page": "1",
		}

		if (len(query) != 0):
			endpoint = endpoint_list["search"]
		else:
			endpoint = endpoint_list["random"]

		response = requests.get(url = self.unsplash_api + endpoint, params = params)
		data = response.json()

		if (len(query) != 0):
			if (str(response.status_code)[:2] == 40):
				self.log.error(f"API Rate limit hit for this hour {datetime.now()}")
				self.log.error(f"Status Code: {response.status_code}")

				response = requests.get(self.dog_api).json()[0]

				embed = discord.Embed(
					title = "Sorry!",
					color = 0xea1010			# Red
				)
				embed.add_field(
					name = "50/50 Requests of this Hour reached. Try again next Hour.",
					value = "Maybe give money to @luciferchase? Anyway here is a cute doggo ❤"
				)
				embed.set_image(url = response["url"])
				await ctx.send(embed = embed)
				return
			
			elif (data["results"] == []):
				self.log.error(f"No photo found for the query : {' '.join(query)}")

				response = requests.get(self.dog_api).json()[0]

				embed = discord.Embed(
					title = "No Photo Found",
					color = 0xea1010			# Red
				)
				embed.add_field(
					name = f"No photo found for the query : `{' '.join(query)}`",
					value = "Maybe change your query? Anyway here is a cute doggo ❤"
				)
				embed.set_image(url = response["url"])
				await ctx.send(embed = embed)
				return

			likes = {}

			for photo in data["results"]:
				likes[photo["id"]] = photo["likes"]
			
			photo_info = [photo for photo in data["results"] if photo["id"] == max(likes)][0]

		# In case there is no particular photo requested, get a random photo
		else:
			photo_info = data

		if (photo_info["description"] == None):
			if (photo_info["alt_description"] != None):
				photo_info["description"] = photo_info["alt_description"]
			else:
				photo_info["description"] = "Photo"

		embed = discord.Embed(
			title = f"{' '.join(query)}".title(),
			description = f'{photo_info["description"][:50]}...',
			url = photo_info["urls"]["regular"],
			color = 0xf5009b					# Pinkish
		)
		embed.set_author(
			name = photo_info["user"]["name"],
			url = f'https://unsplash.com/@{photo_info["user"]["username"]}',
			icon_url = photo_info["user"]["profile_image"]["large"]
		)
		embed.set_thumbnail(url = photo_info["user"]["profile_image"]["large"])
		embed.set_image(url = photo_info["urls"]["full"])
		embed.set_footer(text = f"❤️ {photo_info['likes']}")

		await ctx.send(embed = embed)

	@commands.command()
	async def wallpaper(self, ctx):
		""" Get Bing's daily wallpaper of the day
		"""

		response = requests.get(self.bing_api)
		data = response.json()

		await ctx.send(data["images"][0]["title"])
		
		wallpaper = await ctx.send(f'http://bing.com{data["images"][0]["url"]}')
		await wallpaper.add_reaction("❤️")
		await wallpaper.add_reaction("👍")
		await wallpaper.add_reaction("👎")

	async def send_photo(self, api, ctx = commands.Context):
		response = requests.get(api).json()[0]

		embed = discord.Embed(
			title = "Here is a cute doggo ❤",
			color = 0xf34949			# Red
		)
		embed.set_image(url = response["url"])
		await ctx.send(embed = embed)
			
	@commands.command()
	async def dog(self, ctx):
		""" Get a random dog pic
		"""
		await self.send_photo(self.dog_api)

	@commands.command()
	async def cat(self, ctx):
		""" Get a random cat pic
		"""
		await self.send_photo(self.cat_api)

	@commands.command()
	async def fox(self, ctx):
		""" Get a random fox pic
		"""
		await self.send_photo(self.fox_api)

	@commands.command()
	async def panda(self, ctx):
		""" Get a random panda pic
		"""
		self.send_photo(self.panda_api)

	@commands.command()
	async def redpanda(self, ctx):
		""" Get a random red panda pic
		"""
		await self.send_photo(self.red_panda_api)

	@commands.command(aliases = ["bird"])
	async def birb(self, ctx):
		""" Get a random bird pic
		"""
		await self.send_photo(self.birb_api)

	@commands.command()
	async def koala(self, ctx):
		""" Get a random koala pic
		"""
		await self.send_photo(self.koala_api)
