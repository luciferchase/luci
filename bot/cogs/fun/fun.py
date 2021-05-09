import discord
from discord.ext import commands

import aiohttp
from datetime import datetime

class Fun(commands.Cog):
	"""Various fun commands"""
	def __init__(self, bot):
		self.bot = bot
		# Initialize a session
		self.session = aiohttp.ClientSession()

	@commands.command(aliases = ["nda", "nato"])
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
				message_string += f"{chr(97 + index)}: {phonetics[index]}\n"

		else:
			for letter in args:
				message_string += f"{letter}: {''.join([word for word in phonetics if word[0].lower() == letter])}\n"

		await ctx.send(f"```ml\n{message_string}```")

	
	@commands.command()
	async def catfact(self, ctx):
		"""Get a random fact about cats."""
		async with self.session.get("https://catfact.ninja/fact") as response:
			data = await response.json()
			fact = data["fact"]

			embed = discord.Embed(title = "Catfact ❤", description = fact, color = 0x00ffff)
			await ctx.send(embed = embed)

	
	@commands.command()
	async def dogfact(self, ctx):
		"""Get a random fact about dogs. [Bit slow to run for the first time though (API limitation)]"""
		async with self.session.get("https://dog-facts-api.herokuapp.com/api/v1/resources/dogs?number=1") as response:
			data = await response.json()
			fact = data[0]["fact"]

			embed = discord.Embed(title = "Dogfact ❤", description = fact, color = 0x00ffff)
			await ctx.send(embed = embed)
	
	
	@commands.guild_only()
	@commands.command()
	async def poll(self, ctx, *message):
		"""Do a poll
		Syntax: luci poll <question> |option 1|option 2|option 3|...
		For eg: luci poll Is luci geh? |Yes|No|You are geh|
		You can omit options to make it automatically a two option poll
		"""

		# Delete original message
		await ctx.message.delete()

		message = " ".join(message)
		time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

		# CHeck if there is an actual question given or not
		if (len(message) == 0):
			await ctx.send("Bruh! Send a question atlease 🤦‍♂️")
			# await ctx.invoke(self.bot.get_command("help"), "dm")
			return

		# Get index of question and options separator "|"
		index = message.find("|")

		# Check if there are any options or not
		if (index != -1):
			# Get question and options from the message
			question = message[:message.find("|")]
			options = [option for option in message[message.find("|") + 1:].split("|") if option != ""]

			# Check if there are more than 26 options
			if (len(options) > 20):
				await ctx.send("Bruh! Please give maximum 20 options 🤦‍♂️. You can only react 20 times to a message.")
				return

			reactions = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "J", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", \
			"🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"]

			options_string = ""
			for index in range(len(options)):
				options_string += f"{reactions[index]} {options[index]}\n"

			embed = discord.Embed(
				title = question,
				description = options_string,
				color = 0x00FFFF
			)
			embed.set_footer(text = time)
			embed.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)

			poll_embed = await ctx.send(embed = embed)

			for index in range(len(options)):
				await poll_embed.add_reaction(reactions[index])
			
		# Else by default make a dual option poll
		else:
			question = "".join(message)

			embed = discord.Embed(
				title = question,
				color = 0x00FFFF
			)
			embed.set_footer(text = time)
			embed.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)

			poll_embed = await ctx.send(embed = embed)
			await poll_embed.add_reaction("👍")
			await poll_embed.add_reaction("👎")

	
	@commands.command(aliases = ["emojify", "cry"])
	async def shout(self, ctx, *message):
		"""Convert a message into emojies"""

		# # Delete original message
		# await ctx.message.delete()
		
		final_message = []

		for word in message:
			message_string = ""

			for letter in word:
				message_string += f":regional_indicator_{letter.lower()}: "
			final_message.append(message_string)

		await ctx.send(" ".join(final_message))


	@commands.command()
	async def insult(self, ctx, member: discord.Member = None):
		"""Insult someone. They are really evil though, take care."""

		if (member is None):
			member = ctx.author

		async with self.session.get("https://evilinsult.com/generate_insult.php") as response:
			text = await response.text()

			embed = discord.Embed(
				title = f"{ctx.author.name} insulted {member.name}",
				description = text,
				color = 0xf34949
			)
			await ctx.send(embed = embed)


	@commands.guild_only()
	@commands.command(aliases = ["n"])
	async def nitro(self, ctx, emoji_name):
		"""Send an animated emoji even if you don't have nitro. Send just its name and the bot will send the emote.
		Usage: `luci n nacho`"""

		# # Delete original message
		# await ctx.message.delete()

		# First get all the emojies the bot has access and then Send emoji
		emoji_found = False
		for emoji in ctx.guild.emojis:
			if (emoji.name in emoji_name):
				await ctx.send(emoji.url)
				emoji_found = True

		if (not emoji_found):
			await ctx.send("Emoji not found <a:awkward1:839499334555140157>")