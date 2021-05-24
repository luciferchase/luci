import discord
from discord.ext import commands
from discord.utils import get

from datetime import datetime, timedelta
import logging
import os
import psycopg2
from discordpy_slash import slash

from cogs.botstatus.botstatus import Botstatus

class Core(commands.Cog):
	"""Core commands. Most of them are owner only."""
	def __init__(self, bot):
		self.bot = bot

		# Set up database
		DATABASE_URL = os.environ["DATABASE_URL"]

		self.dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
		self.cursor = self.dbcon.cursor()

	# Events
	@commands.Cog.listener()	
	async def on_ready(self):
		print("Connected to discord")

		# Wait till bot has done all its internal stuff
		await self.bot.wait_until_ready()

		# Set status
		await Botstatus(self.bot).set_botstatus_on_ready()

		# Sync slash commands
		# await slash.sync_all_commands(self.bot)

	@commands.Cog.listener()
	async def on_member_join(self, member):
		if (member.guild.id != 738731754885480468):
			return

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
		if (member.guild.id != 738731754885480468):
			return
		
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
		for guild in self.bot.guilds:
			if (guild.id not in [738731754885480468]):
				return

		# Create a dm with me
		luci = self.bot.get_user(707557256220115035)
		dm = await luci.create_dm()

		embed = discord.Embed(
			title = f"Invite Created by {invite.inviter}",
			description = f"Channel: {invite.channel}",
			color = 0xf34949
		)
		embed.add_footer(text = invite.created_at)
		await dm.send(embed = embed)

	@commands.Cog.listener()
	async def on_message(self, message):
		# If the message is from the bot itself then return
		if (message.author == self.bot.user):
			return

		# Make a variable about me
		luci = self.bot.get_user(707557256220115035)
		
		# Forward all messages to me if the message is not from a guils, or by a bot or by me
		if (message.guild is None and not message.author.bot and message.author != luci):
			dm_channel = await luci.create_dm()
			
			embed = discord.Embed(title = "Direct Message", description = message.content, color = 0x00FFFF)
			embed.set_author(name = message.author.name, icon_url = message.author.avatar_url)
			embed.set_footer(text = message.created_at)

			# Send attachments
			if (message.attachments != None):
				try:
					embed.set_image(url = message.attachments[0].url)
				except:
					pass

			await dm_channel.send(embed = embed)
			await message.channel.send(f"Message sent to {luci.name}")

	# Add last 5 deleted message to database
	@commands.Cog.listener()
	async def on_message_delete(self, message):
		if (message.guild.id != 738731754885480468):
			return
		
		# Check if the message was a poll or shout which was automatically deleted by the bot
		# Check the message is deleted by an actual user and not by a bot
		if (message.author.bot == True or \
			"luci poll" in message.content.lower() or "luci shout" in message.content.lower()):
			return

		# Create table
		query = """CREATE TABLE IF NOT EXISTS snipe(
				mssg_id 	TEXT 	NOT NULL,
				author_id 	BIGINT 	NOT NULL,
				channel_id 	BIGINT 	NOT NULL,
				deleted_on	TEXT 	NOT NULL,
				deleted_at 	TEXT	NOT NULL)"""
		self.cursor.execute(query)
		self.dbcon.commit()

		# Fetch data from the table according to channel id
		self.cursor.execute(f"SELECT * FROM snipe WHERE channel_id = {message.channel.id}")
		data = self.cursor.fetchall()

		# Configure date, time
		deleted_on = datetime.now().strftime("%m/%d/%Y")

		# Add 5:30 hours to GMT
		deleted_at = (datetime.now() + timedelta(hours = 5, minutes = 30)).strftime("%H:%M:%S")
		
		# Check if there are more than 5 messages in the database
		if (len(data) >= 5):
			# Remove the oldest message
			del data[0]

			# Add new message to the top of the stack
			mssg, author, channel= message.content, message.author.id, message.channel.id
			data.append((mssg, author, channel, deleted_on, deleted_at))
		
		else:
			mssg, author, channel= message.content, message.author.id, message.channel.id
			data.append((mssg, author, channel, deleted_on, deleted_at))
			
		# Update database
		self.cursor.execute(f"DELETE FROM snipe WHERE channel_id = {message.channel.id}")

		for i in data:
			self.cursor.execute("INSERT INTO snipe VALUES {}".format(i))

	# Fun, "for all" commands
	@commands.command()
	async def ping(self, ctx):
		"""Ping Pong"""
		await ctx.send(f"🏓 Pong in {str(round(self.bot.latency, 3))} s")

	@commands.command()
	async def invite(self, ctx):
		"""Invite bot to your server"""
		nacho = self.bot.get_emoji(839499460874862655)

		embed = discord.Embed(
			title = "[Invite Link](https://discord.com/api/oauth2/authorize?client_id=836213550384545852&permissions=3221744704&scope=bot)",
			description = f"Thank you for adding me to your server {nacho}",
		)
		ctx.send(embed = embed)

	@commands.command(aliases = ["pm"])
	async def dm(self, ctx, userid: int, *message: str):
		"""DM a user
		Syntax: luci dm 707557256220115035 you are geh"""
		if (userid is None or message is None):
			await ctx.send("Bruh! Give a user atlease")
			# await ctx.invoke(self.bot.get_command("help"), "dm")
		try:
			user_to_dm = self.bot.get_user(int(userid))
			dm_channel = await user_to_dm.create_dm()
		except:
			await ctx.send("User not found. Is the user even real?")
			# await ctx.invoke(self.bot.get_command("help"), "dm")
			return

		message = " ".join(message)

		embed = discord.Embed(title = "Direct Message", description = message)
		embed.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)
		embed.set_footer(text = ctx.message.created_at)

		try:
			await dm_channel.send(embed = embed)
			await ctx.send(f"DM Sent successfully to {user_to_dm.name}")
		except:
			await ctx.send("DM not sent. Have you done eveything correctly?")
			# await ctx.invoke(self.bot.get_command("help"), "dm")


	@commands.guild_only()
	@commands.command()
	async def snipe(self, ctx, number = 1):
		for guild in self.bot.guilds:
			if (guild.id not in [738731754885480468]):
				return
		
		"""See upto 5 last deleted message
		For eg: `luci snipe` gets the last deleted message
		Also:  `luci snipe 2` gets the second last deleted message and so on."""
		
		# Check if number is not more 5
		if (number > 5):
			await ctx.send("Bruh! Can get last 5 messages only. Get a life bro 🤦‍♂️")
			return

		# Fetch last deleted message from database
		self.cursor.execute(f"SELECT * FROM snipe WHERE channel_id = {ctx.channel.id}")
		data = self.cursor.fetchall()

		# If there are no messages deleted in this channel
		if (data == []):
			await ctx.send(embed = discord.Embed(title = "No messages deleted in this channel", color = 0xf34949))
			return

		# Configure channel where message was deleted
		channel = self.bot.get_channel(data[-number][2])

		# Fetch deleted message author
		author = self.bot.get_user(data[-number][1])

		embed = discord.Embed(title = data[-number][0], color = 0xf34949)
		embed.add_field(
			name = "Deleted on:",
			value = f"{data[-number][3]} | {data[-number][4]}",
			inline = True
		)
		embed.add_field(
			name = "In:",
			value = channel.mention,
			inline = True
		)
		embed.add_field(
			name = "By:",
			value = author.mention,
			inline = True
		)
		embed.set_footer(
		 	text = f"Asked by {ctx.author.name}#{ctx.author.discriminator}", 
		 	icon_url = ctx.author.avatar_url
		)
		embed.set_author(name = f"Author: {author.name}", icon_url = author.avatar_url)
		await ctx.send(embed = embed)

	
	# Dev commands, "owner only"
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
		try:
			self.dbcon.rollback()
			await ctx.send("Successfully rollbacked to last transaction")
		except:
			await ctx.send("Rollback not successfull. Check logs.")
			return

	
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