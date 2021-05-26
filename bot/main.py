# Install all dependencies
import discord
from discord.ext import commands
from pretty_help import DefaultMenu, PrettyHelp

import sys
import os
import logging
import requests
import psycopg2

# Install all cogs
# from cogs.afk import afk
from cogs.aki import aki
from cogs.avatar import avatar
from cogs.bigmoji import bigmoji
from cogs.botstatus import botstatus
from cogs.comics import comics
from cogs.core import core, schedule_jobs
from cogs.conversationgames import conversationgames
from cogs.fun import fun
# from cogs.ipl import ipl
from cogs.math import math
from cogs.meme import meme
from cogs.moderation import moderation
from cogs.photo import photo
from cogs.quiz import quiz
# from cogs.testing import testing
from cogs.tictactoe import tictactoe

# Get Members intent
intents = discord.Intents.all()

# Configure help menu
menu = DefaultMenu(page_left = "⬅️", page_right = "➡️")

# Configure the bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = commands.Bot(
	command_prefix = ["luci ", "Luci "], 
	case_insensitive = True, 
	strip_after_prefix = False, 
	intents = intents, 
	self_bot = False, 
	owner_id = 707557256220115035,  
	help_command = PrettyHelp(color = 0xf34949, sort_commands = True),
	description = "A General-Purpose Discord Bot Created by luciferchase#6310"
)

# Set up logging
logging.basicConfig(level = logging.WARNING)

# Register Cogs
# bot.add_cog(afk.AFK(bot))
bot.add_cog(aki.Aki(bot))
bot.add_cog(avatar.Avatar())
bot.add_cog(bigmoji.Bigmoji(bot))
bot.add_cog(botstatus.Botstatus(bot))
bot.add_cog(comics.Comics(bot))
bot.add_cog(core.Core(bot))
# bot.add_cog(core.Help(bot))
bot.add_cog(conversationgames.ConversationGames())
bot.add_cog(fun.Fun(bot))
# bot.add_cog(ipl.IPL(bot))
bot.add_cog(math.Math(bot))
bot.add_cog(meme.Meme())
bot.add_cog(moderation.Moderation(bot))
bot.add_cog(photo.Photo())
bot.add_cog(quiz.Quiz(bot))
# bot.add_cog(testing.Testing())
bot.add_cog(tictactoe.TTT(bot))

# Start scheduled commands
scheduler = schedule_jobs.Scheduler(bot).schedule()
scheduler.start()

# Run the bot
bot.run(BOT_TOKEN)