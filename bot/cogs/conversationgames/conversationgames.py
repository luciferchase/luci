import discord
from discord.ext import commands

import random


class ConversationGames(commands.Cog):
	"""Conversation Games"""
		
	@commands.command(aliases = ["wyr"])
	@commands.bot_has_permissions(embed_links = True)
	async def wouldyourather(self, ctx):
		"""Would you rather?"""

		with open("wyr.json", "r") as wyr:
			questions = json.load(wyr)

		# Build Embed
		embed = discord.Embed()
		embed.title = "Would you rather.."
		embed.description = random.choice(questions)
		await ctx.send(embed = embed)

	@commands.command(aliases = ["nhie"])
	@commands.bot_has_permissions(embed_links = True)
	async def neverhaveiever(self, ctx):
		"""Never have I"""

		with open("nhie.json", "r") as nhie:
			questions = json.load(nhie)

		# Build Embed
		embed = discord.Embed()
		embed.title = "Never have I ever.."
		embed.description = random.choice(questions)
		await ctx.send(embed = embed)

	@commands.command()
	@commands.bot_has_permissions(embed_links = True)
	async def truth(self, ctx, *, user: discord.Member):
		"""Ask a truth question to users!"""
		
		with open("truths.json", "r") as truths:
			questions = json.load(truths)

		# Set author
		author = ctx.message.author

		# Get and pick random user
		member_list = len(ctx.guild.members)
		random_number = randint(0, member_list - 1)
		random_member = ctx.guild.members[random_number].mention

		# Build Embed
		embed = discord.Embed()
		embed.title = f"{author.name} asked {user.name}"
		embed.description = random.choice(questions).format(name = random_member)
		await ctx.send(embed = embed)

	@commands.command()
	@commands.bot_has_permissions(embed_links = True)
	async def dare(self, ctx, *, user: discord.Member):
		"""Dare someone!"""

		with open("dares.json", "r") as dares:
			questions = json.load(dares)

		# Set author
		author = ctx.message.author

		# Get and pick random user
		member_list = len(ctx.guild.members)
		random_number = randint(0, member_list - 1)
		random_member = ctx.guild.members[random_number].mention

	# Build Embed
	embed = discord.Embed()
	embed.title = f"{author.name} dared {user.name}"
	embed.description = random.choice(questions).format(name = random_member)
	await ctx.send(embed = embed)
