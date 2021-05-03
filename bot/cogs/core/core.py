import discord
from discord.ext import commands

import logging
import os
import psycopg2

from cogs.core.botstatus import Botstatus

class Core(commands.Cog):
	"""Core commands. Most of them are owner only."""
	def __init__(self, bot):
		self.bot = bot

		# Set up database
		DATABASE_URL = os.environ["DATABASE_URL"]

		self.dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		self.cursor = self.dbcon.cursor()

	# Core Commands
	@commands.Cog.listener()	
	async def on_ready(self):
		print("Connected to discord")

		# Wait till bot has done all its internal stuff
		await self.bot.wait_until_ready()

		# Set status
		await Botstatus(self.bot).set_botstatus_on_ready()

	@commands.Cog.listener()
	async def on_member_join(self, member):
		channel = member.guild.system_channel
			
		if channel is not None:
			await channel.send(member.mention)
			
			embed = discord.Embed(
				title = f"Welcome {member.name}", 
				description = f"Aap aayen hai {member.guild.name} ki bagiyaaan mein \n"
								"phool khile hai gulshan gulshan \n"
								"Phulllll khile hai gulshan gulshaannnnnnnnn \n"
								"Phool khile hai iss bagiyaan mein \n"
								"Aap aayein hai gulshan gulshan",
				color = 0xf34949
			) 
			embed.set_thumbnail(url = member.guild.icon_url)
			embed.set_image(url = member.avatar_url)
			await channel.send(embed = embed)

	@commands.Cog.listener()
	async def on_member_remove(self, member):
		channel = member.guild.system_channel
			
		if channel is not None:
			embed = discord.Embed(
				title = "Sed lyf",
				description = f"{member.name} has left {member.guild.name} 🥺",
				color = 0xf34949
			)
			embed.set_thumbnail(url = member.guild.icon_url)
			embed.set_image(url = member.avatar_url)
			await channel.send(embed = embed)

	@commands.Cog.listener()
	async def on_invite_create(self, invite):
		# Create a dm with me
		luci = self.bot.get_user(707557256220115035)
		dm = await luci.create_dm()

		embed = discord.Embed(
			title = f"Invite Created by {invite.inviter}",
			description = f"Channel: {invite.channel}",
			color = 0xf34949
		)
		await dm.send(embed = embed)

	# Add last 5 deleted message to database
	@commands.Cog.listener()
	async def on_message_delete(self, message):
		# Check the message is deleted by an actual user and not by a bot
		if (message.author.bot == True):
			return

		# Create table
		query = """CREATE TABLE IF NOT EXISTS snipe(
				mssg_id 	TEXT 		NOT NULL,
				author_id 	BIGINT 		NOT NULL,
				channel_id 	BIGINT 		NOT NULL,
				deleted_at	TIMESTAMP 	NOT NULL)"""
		self.cursor.execute(query)
		self.dbcon.commit()

		# Fetch data from the table according to channel id
		self.cursor.execute(f"SELECT * FROM snipe WHERE channel_id = {message.channel.id}")
		data = self.cursor.fetchall()

		print(message.created_at)
		
		# Check if there are more than 5 messages in the database
		if (len(data) >= 5):
			# Remove the oldest message
			del data[0]

			# Add new message to the top of the stack
			mssg, author, channel, timestamp = message.content, message.author.id, \
			message.channel.id, message.created_at
			data.append((mssg, author, channel, timestamp))
		
		else:
			mssg, author, channel, timestamp = message.content, message.author.id, \
			message.channel.id, message.created_at
			data.append((mssg, author, channel, timestamp))
			
		# Update database
		self.cursor.execute(f"DELETE FROM snipe WHERE channel_id = {message.channel.id}")

		for i in data:
			self.cursor.execute("INSERT INTO snipe VALUES {}".format(i))

	@commands.command()
	async def ping(self, ctx) :
		"""Ping Pong"""
		await ctx.send(f"🏓 Pong in {str(round(self.bot.latency, 3))} s")

	@commands.is_owner()
	@commands.command(hidden = True)
	async def sql(self, ctx, *query):
		log = logging.getLogger("sql")
		
		# Create a dm with me
		luci = self.bot.get_user(707557256220115035)
		dm = await luci.create_dm()

		query = " ".join(query)
		print("Executing query:", query)
		try:
			self.cursor.execute(query)
			await ctx.send("Query executed successfully")
			try:
				self.dbcon.commit()
			except:
				pass
		except:
			log.error(f"{query} not executed successfully")
			await ctx.send("Query not executed. Check logs.")

		try:
			data = self.cursor.fetchall()
			print(data)
			await ctx.send("Data sent in DM")
			await dm.send(data)
		except:
			pass

	# Command to rollback to last transaction when there is a issue with psycopg2
	@commands.is_owner()
	@commands.command(hidden = True)
	async def rollback(self, ctx):
		self.dbcon.rollback()

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
	async def botavatar(self, ctx, which = ""):
		"""Change bot name.
		"""
		log = logging.getLogger("botavatar")
		
		with open(f"/app/bot/avatars/avatar{which}.png", "rb") as avatar:
			avatar_image = avatar.read()
			try:
				await self.bot.user.edit(avatar = avatar_image)
				await ctx.send("Bot avatar chaned successfully")
			except:
				log.error("Cannot change bot name")
				await ctx.send("Cannot change bot avatar. Check logs.")

	@commands.command()
	async def snipe(self, ctx, number = 1):
		"""See upto last deleted message
		For eg: `luci snipe` gets the last deleted message
		Also:  `luci snipe 2` gets the second last deleted message and so on."""
		
		# Fetch last deleted message from database
		self.cursor.execute(f"SELECT * FROM snipe WHERE channel_id = {ctx.channel.id}")
		data = self.cursor.fetchall()

		# Fetch deleted message author
		author = self.bot.get_user(data[-number][1])
		embed = discord.Embed(
			title = ":dart: Sniped",
			description = data[-number][0]
		)
		embed.set_footer(
		 	text = f"Asked by {ctx.author.name}#{ctx.author.discriminator}", 
		 	icon_url = ctx.author.avatar_url
		)
		embed.set_author(name = f"<@{author.mention}>")
		await ctx.send(embed = embed)




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
