import discord
from discord.ext import commands
from TagScriptEngine import Interpreter, adapter, block

import aiohttp
import json
import logging
import time


class Math(commands.Cog):
	"""Do math"""

	def __init__(self, bot):
		self.bot = bot
		blocks = [
			block.MathBlock(),
			block.RandomBlock(),
			block.RangeBlock(),
		]
		self.engine = Interpreter(blocks)

		# Initialize a session
		self.session = aiohttp.ClientSession()
	
	@commands.command()
	async def math(self, ctx, *expression):
		""" Solve a math expression. Supports very complex problems too.
			For eg. `luci math sin(pi/4)`
		"""
		log = logging.getLogger("math")

		if (expression == ""):
			embed = discord.Embed(
			color = 0xf34949,									# Red							
			title = "Input A Expression"
			)
			await ctx.send(embed = embed)
			return

		start = time.monotonic()

		api = "http://api.mathjs.org/v4/"
		params = {
			"expr": "".join(expression) 
		}

		async with self.session.get(api, params = params) as response:
			end = time.monotonic()

			if (str(response.status) != 200):
				log.info(expression)
				log.error(response.text)
				return

			embed = discord.Embed(
				color = 0xf34949,									# Red					
				title = await response.text
			)
			embed.add_field(
				name = "Your Input:",
				value = f'`{"".join(expression)}`',
				inline = True
			)
			embed.add_field(
				name = "Answer:",
				value = f"`{await response.text}`",
				inline = True
			)
			embed.set_footer(text = f"Calculated in {round((end - start) * 1000, 3)} ms")
			await ctx.send(embed = embed)

	@commands.command(aliases=["calc"])
	async def calculate(self, ctx, *, query):
		""" Faster but sometimes does not work.
		"""
		
		query = query.replace(",", "")
		engine_input = "{m:" + query + "}"
		start = time.monotonic()
		output = self.engine.process(engine_input)
		end = time.monotonic()

		output_string = output.body.replace("{m:", "").replace("}", "")
		embed = discord.Embed(
			color = 0xf34949,
			title = f"Input: `{query}`",
			description = f"Output: `{output_string}`",
		)
		embed.set_footer(text = f"Calculated in {round((end - start) * 1000, 3)} ms")
		await ctx.send(embed = embed)
