# Install all dependencies
import discord
from discord.ext import commands

import sys
import os
import logging

# Install all cogs
from cogs.akinator import akinator
from cogs.avatar import avatar
from cogs.conversationgames import conversationgames
from cogs.core import core
from cogs.ipl import ipl
from cogs.math import math
from cogs.meme import meme
from cogs.photo import photo


# Configure the bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = commands.Bot(command_prefix = "luci ")

logging.basicConfig(level = logging.WARNING)

# Get Members intent
intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents = intents)

# Register Cogs
bot.add_cog(akinator.Aki(bot))
bot.add_cog(avatar.Avatar())
bot.add_cog(conversationgames.ConversationGames())
bot.add_cog(core.Core(bot))
bot.add_cog(ipl.IPL(bot))
bot.add_cog(math.Math(bot))
bot.add_cog(meme.Meme())
bot.add_cog(photo.Photo())

# Run the bot
bot.run(BOT_TOKEN)