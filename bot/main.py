# Install all dependencies
import discord
from discord.ext import commands

import sys
import os
import logging

# Install all cogs
from cogs.avatar import avatar
from cogs.conversationgames import conversationgames
from cogs.ipl import ipl
from cogs.math import math
from cogs.meme import meme
from cogs.photo import photo


# Configure the bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = commands.Bot(command_prefix = "luci ")

logging.basicConfig(level = logging.DEBUG)

# Register Cogs
bot.add_cog(avatar.Avatar(bot))
bot.add_cog(conversationgames.ConversationGames(bot))
bot.add_cog(ipl.IPL(bot))
bot.add_cog(math.Math(bot))
bot.add_cog(meme.Meme())
bot.add_cog(photo.Photo())

# Core Commands
@bot.event
async def on_ready():
	try:
		await bot.change_presence(
			status = discord.Status.idle, 
			activity = discord.Activity(
					type = discord.ActivityType.listening,
					name = "your heartbeats"
				)
		)
		print("Activity set successfully")
	except:
		print("Cannot set activity")
	print("Connected to discord")

@bot.command()
async def ping(ctx) :
	await ctx.send(f"🏓 Pong with {str(round(bot.latency, 2))}")

bot.run(BOT_TOKEN)