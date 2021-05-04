import discord
from discord.ext import commands


class Fun(commands.Cog):
	"""Various fun commands"""

	@commands.command(aliases = ["nda"])
	async def alphanato(self, ctx, *args = "all"):
		"""Get military phonetics of every letter in english alphabet.
		Usage: You can get all the phonetics by simply calling `luci nda` or `luci alphanato`
		
		You can also get phonetics for a particular letter or multiple letter (separated by space) by doing:
		`luci nda l` or `luci nda l m n o`"""
		
		phonetics = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf", "Hotel", "India", "Juliett", \
		"Kilo", "Lima", "Mike", "November", "Oscar", "Papa", "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor", \
		"Whiskey", "X-Ray", "Yankee", "Zulu"]

		message_string = ""

		if (args == "all"):
			for index in range(26):
				message_string += f"{chr(97 + index)}: {phonetics[index]}\n"

		else:
			for letter in args:
				message_string += f"{letter}: {"".join([word for word in phonetics if word[0].lower() == letter])}\n"

		await ctx.send(f"```ml{message_string}```")
