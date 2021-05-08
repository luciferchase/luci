import discord
from discord.ext import commands
from TagScriptEngine import Interpreter, adapter, block

import aiohttp
import json
import logging
import time
from urllib import parse


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

			if (response.status != 200):
				log.info(expression)
				log.error(await response.text())
				return

			embed = discord.Embed(
				color = 0xf34949,									# Red					
				title = await response.text()
			)
			embed.add_field(
				name = "Your Input:",
				value = f'`{"".join(expression)}`',
				inline = True
			)
			embed.add_field(
				name = "Answer:",
				value = f"`{await response.text()}`",
				inline = True
			)
			embed.set_footer(text = f"Calculated in {round((end - start) * 1000, 3)} ms")
			await ctx.send(embed = embed)

	@commands.command(aliases=["calc"])
	async def calculate(self, ctx, *, query):
		""" Faster but sometimes does not work."""
		
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


	async def get_result(self, ctx, operation, expression):
		# First properly encode expression
		# Change "/" to (over) because the api says so
		if ("/" in expression):
			expression = expression.replace("/", "(over)")

		# Encode the url now
		encoded_expression = parse.quote(expression)
		api = "https://newton.now.sh/api/v2"

		start = time.monotonic()
		async with self.session.get(f"{api}/{operation}/{encoded_expression}") as response:
			data = await response.json()

			if ("error" in data.keys()):
				# Get coolcry emoji
				coolcry = self.bot.get_emoji(780445565476798475)

				embed = discord.Embed(
					title = f"Sorry! But the server was unable to solve the expression {coolcry}",
					color = 0xf34949
				)
				return embed

			result = data["result"]
			end = time.monotonic()

			embed = discord.Embed(
				color = 0xf34949,									# Red					
				title = result
			)
			embed.add_field(
				name = "Your Input:",
				value = f'`{expression.replace("(over)", "/")}`',
				inline = True
			)
			embed.add_field(
				name = "Answer:",
				value = f"`{result}`",
				inline = True
			)
			embed.set_footer(text = f"Calculated in {round((end - start) * 1000, 3)} ms")
			return embed

	
	@commands.command(aliases = ["factor"])
	async def factorise(self, ctx, *expression):
		"""Factorise a polynomial equation. Please put tan(x) instead of tanx and so on for all trigonametric functions.
		Usage: `luci factorise x^2 + 2x`"""
		expression = "".join(expression)

		loading = await ctx.send("Calculating...")
		await ctx.trigger_typing()

		embed = await self.get_result(ctx = ctx, operation = "factor", expression = expression)

		# First delete the calculating message
		await loading.delete()
		await ctx.send(embed = embed)


	@commands.command(aliases = ["derivation", "differentiate"])
	async def derive(self, ctx, *expression):
		"""Differentiate a polynomial. Please put tan(x) instead of tanx and so on for all trigonametric functions.
		Usage: `luci derive x^2 + 2x`"""
		expression = "".join(expression)

		loading = await ctx.send("Calculating...")
		await ctx.trigger_typing()

		embed = await self.get_result(ctx = ctx, operation = "derive", expression = expression)

		# First delete the calculating message
		await loading.delete()
		await ctx.send(embed = embed)


	@commands.command(aliases = ["integration"])
	async def integrate(self, ctx, *expression):
		"""Integrate a polynomial. Please put tan(x) instead of tanx and so on for all trigonametric functions.
		Usage: `luci integrate x^2 + 2x`"""
		expression = "".join(expression)

		loading = await ctx.send("Calculating...")
		await ctx.trigger_typing()

		embed = await self.get_result(ctx = ctx, operation = "integrate", expression = expression)

		# First delete the calculating message
		await loading.delete()
		await ctx.send(embed = embed)


	@commands.command(aliases = ["solution", "zeroes", "roots"])
	async def solve(self, ctx, *expression):
		"""Find roots of a polynomial. Please put tan(x) instead of tanx and so on for all trigonametric functions.
		Usage: `luci roots x^2 + 2x`"""
		expression = "".join(expression)

		loading = await ctx.send("Calculating...")
		await ctx.trigger_typing()

		embed = await self.get_result(ctx = ctx, operation = "zeroes", expression = expression)

		# First delete the calculating message
		await loading.delete()
		await ctx.send(embed = embed)


	@commands.command()
	async def tangent(self, ctx, *expression):
		"""Find tangent of a curve at a point [Eg: `luci tangent 2|x^3`. See `luci help tangent`]. Please put tan(x) instead of tanx and so on for all trigonametric functions.
		Usage: `luci tangent 2|x^3` # Here 2 is the point where tangent is to be find"""
		expression = "".join(expression)

		loading = await ctx.send("Calculating...")
		await ctx.trigger_typing()

		embed = await self.get_result(ctx = ctx, operation = "tangent", expression = expression)

		# First delete the calculating message
		await loading.delete()
		await ctx.send(embed = embed)


	@commands.command(name = "area", aliases = ["area under the curve", "definite integration"])
	async def definite_integral(self, ctx, *expression):
		"""Do definite integration on a polynomial [Eg: `luci area 2:4|x^3`. See `luci help area`]. Please put tan(x) instead of tanx and so on for all trigonametric functions.
		Usage: `luci area 2:4|x^3` # Here area is to be calulated from 2 to 4"""
		expression = "".join(expression)

		loading = await ctx.send("Calculating...")
		await ctx.trigger_typing()

		embed = await self.get_result(ctx = ctx, operation = "area", expression = expression)

		# First delete the calculating message
		await loading.delete()
		await ctx.send(embed = embed)
