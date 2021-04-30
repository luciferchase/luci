import discord
from discord.ext import commands

import logging
import os
import psycopg2

class Core(commands.Cog):
	"""Core commands. Most of them are owner only."""
	def __init__(self, bot):
		self.bot = bot	

	@commands.command()
	async def ping(self, ctx) :
		"""Ping Pong"""
		await ctx.send(f"🏓 Pong with {str(round(bot.latency, 3))}")

	@commands.is_owner()
	@commands.command(hidden = True)
	async def sql(self, ctx, *query):
		log = logging.getLogger("sql")

		DATABASE_URL = os.environ["DATABASE_URL"]

		dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		cursor = dbcon.cursor()

		query = " ".join(query)
		print("Executing query:", query)
		try:
			cursor.execute(query)
			await ctx.send("Query executed successfully")
			try:
				dbcon.commit()
			except:
				pass
		except:
			log.error(f"{query} not executed successfully")
			await ctx.send("Query not executed. Check logs.")

		try:
			data = cursor.fetchall()
			print(data)
			await ctx.send(data)
		except:
			pass

	@commands.is_owner()
	@commands.command(hidden = True, aliases = ["status", "bs"])
	async def botstatus(self, ctx, *query):
		"""Set botstatus `luci <status> <activity> <text>`
		`status` can be: online[o], idle[i], dnd[d]
		`activity` can be : playing[p], listening[l], watching[w], competing[c]
		"""
		log = logging.getLogger("botstatus")

		status, activity, *text = query
		text = " ".join(text)

		DATABASE_URL = os.environ["DATABASE_URL"]

		dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		cursor = dbcon.cursor()

		query = """CREATE TABLE IF NOT EXISTS botstatus(
				status		TEXT	NOT NULL,
				activity 	TEXT,
				name 		TEXT)"""
		cursor.execute(query)
		dbcon.commit()

		cursor.execute("DELETE FROM botstatus")
		dbcon.commit()

		query = f"""INSERT INTO botstatus VALUES
				('{status}', '{activity}', '{text}')"""
		cursor.execute(query)
		dbcon.commit()

		if (status[0] == "o"):
			status_class = discord.Status.online
		elif (status[0] == "i"):
			status_class = discord.Status.idle
		elif (status[0] == "d"):
			status_class = discord.Status.dnd

		if (activity[0] == "p"):
			activity_type = discord.Game(name = text)
		elif (activity[0] == "l"):
			activity_type = discord.Activity(
					type = discord.ActivityType.listening,
					name = text
					)
		elif (activity[0] == "w"):
			activity_type = discord.Activity(
					type = discord.ActivityType.watching,
					name = text
					)
		elif (activity[0] == "c"):
			activity_type = discord.Activity(
					type = discord.ActivityType.competing,
					name = text
					)
		try:
			await self.bot.change_presence(
				status = status_class, 
				activity = activity_type
				)
			print("Activity set successfully")
			await ctx.send("Activity set successfully")
		except:
			log.warning("Cannot set activity")
			await ctx.send("Cannot set activity")

	@commands.is_owner()
	@commands.command(hidden = True)
	async def botname(self, ctx, name):
		"""Change bot name.
		   Syntax: `luci botname <name>`
		"""
		log = logging.getLogger("botname")
		try:
			await self.bot.user.edit(username = name)
			await ctx.send("Bot name changed successfully")
		except:
			log.error("Cannot change bot name")
			await ctx.send("Error. Bot name not changed. Check logs.")

	@commands.is_owner()
	@commands.command(hidden = True)
	async def botavatar(self, ctx):
		"""Change bot name. Not working tho.
		"""
		log = logging.getLogger("botavatar")
		with open("/app/bot/avatar.png", "rb") as avatar:
			try:
				await self.bot.user.edit(avatar = avatar)
				await ctx.send("Bot avatar chaned successfully")
			except:
				log.error("Cannot change bot name")
				await ctx.send("Cannot change bot avatar. Check logs.")

# Not in use though
class Help(commands.Cog):
	"""
	Sends this help message
	"""

	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def help(self, ctx, *input):
		"""Shows all modules of that bot"""
	
		prefix = "luci "
		owner = 707557256220115035
		owner_name = "luciferchase#6310"

		# checks if cog parameter was given
		# if not: sending all modules and commands not associated with a cog
		if not input:
			# checks if owner is on this server - used to 'tag' owner
			try:
				owner = ctx.guild.get_member(owner).mention

			except AttributeError as error:
				owner = owner

			# starting to build embed
			embed = discord.Embed(
				title = "Commands and modules", 
				color = discord.Color.blue(),
				description = f"Use `{prefix}help <module>` to gain more information about that module 😁"
			)

			# iterating trough cogs, gathering descriptions
			cogs_desc = ""
			for cog in self.bot.cogs:
				cogs_desc += f"`{cog}` {self.bot.cogs[cog].__doc__}\n"

			# adding 'list' of cogs to embed
			embed.add_field(
				name = "Modules", 
				value = cogs_desc, 
				inline = False
			)

			# integrating trough uncategorized commands
			commands_desc = ""
			for command in self.bot.walk_commands():
				# if cog not in a cog
				# listing command if cog name is None and command isn't hidden
				if not command.cog_name and not command.hidden:
					commands_desc += f"{command.name} - {command.help}\n"

			# adding those commands to embed
			if commands_desc:
				embed.add_field(
					name = "Not belonging to a module",
					value = commands_desc, 
					inline = False
				)
			embed.set_footer(text = f"{owner}")

		# block called when one cog-name is given
		# trying to find matching cog and it's commands
		elif len(input) == 1:

			# iterating trough cogs
			for cog in self.bot.cogs:
				# check if cog is the matching one
				if cog.lower() == input[0].lower():

					# making title - getting description from doc-string below class
					embed = discord.Embed(
						title = f"{cog} - Commands", 
						description = self.bot.cogs[cog].__doc__,
						color=discord.Color.green()
					)

					# getting commands from cog
					for command in self.bot.get_cog(cog).get_commands():
						# if cog is not hidden
						if not command.hidden:
							embed.add_field(
								name = f"`{prefix}{command.name}`", 
								value = command.help, 
								inline = False
							)
					# found cog - breaking loop
					break

			# if input not found
			# yes, for-loops have an else statement, it's called when no 'break' was issued
			else:
				embed = discord.Embed(
					title="What's that?!",
					description = f"I've never heard from a module called `{input[0]}` before :scream:",
					color=discord.Color.orange()
				)

		# too many cogs requested - only one at a time allowed
		elif len(input) > 1:
			embed = discord.Embed(
				title = "That's too much.",
				description = "Please request only one module at once :sweat_smile:",
				color = discord.Color.orange()
			)

		else:
			embed = discord.Embed(
				title = "It's a magical place.",
				description = "I don't know how you got here. But I didn't see this coming at all.\n"
								"Would you please be so kind to report that issue to me {}\n"
								"Thank you! ~ Lucifer Chase".format(owner),
				color = discord.Color.red())

		# sending reply embed using our own function defined above
		await ctx.send(embed = embed)
