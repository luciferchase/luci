import discord
from discord.ext import commands

import requests


class Fun(commands.Cog):
	"""Various fun commands"""

	@commands.command(aliases = ["nda"])
	async def alphanato(self, ctx, *args):
		"""Get military phonetics of every letter in english alphabet.
		Usage: You can get all the phonetics by simply calling `luci nda` or `luci alphanato`
		
		You can also get phonetics for a particular letter or multiple letter (separated by space) by doing:
		`luci nda l` or `luci nda l m n o`"""
		
		phonetics = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India", "Juliett", \
		"Kilo", "Lima", "Mike", "November", "Oscar", "Papa", "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor", \
		"Whiskey", "X-Ray", "Yankee", "Zulu"]

		message_string = ""

		if (args == ()):
			for index in range(26):
				message_string += f"{chr(65 + index)}: {phonetics[index]}\n"

		else:
			for letter in args:
				message_string += f"{letter}: {''.join([word for word in phonetics if word[0].lower() == letter])}\n"

		await ctx.send(f"```ml\n{message_string}```")

	@commands.command()
	async def catfact(self, ctx):
		"""Get a random catfact"""

		fact = requests.get("https://catfact.ninja/fact").json()["fact"]
		
		embed = discord.Embed(title = "Catfact ❤", description = fact, color = 0x00ffff)
		await ctx.send(embed = embed)