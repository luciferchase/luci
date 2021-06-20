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
from cogs.aki import aki
from cogs.bigmoji import bigmoji
# from cogs.birthday import birthday
from cogs.botstatus import botstatus
from cogs.comics import comics
from cogs.connect4 import connect4
from cogs.conversationgames import conversationgames
from cogs.core import core, schedule_jobs
from cogs.covid import covid
from cogs.fun import fun
from cogs.hangman import hangman
# from cogs.ipl import ipl
from cogs.math import math
from cogs.meme import meme
from cogs.moderation import moderation
from cogs.music import music
from cogs.photo import photo
from cogs.starboard import starboard
from cogs.qtopia import qtopia
from cogs.quiz import quiz
from cogs.tictactoe import tictactoe
from cogs.timezone import timezone

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
	owner_id = 563416794329514006,  
	help_command = PrettyHelp(color = 0xf34949, sort_commands = True),
	description = "A General-Purpose Discord Bot Created by luciferchase#6310"
)

# Set up logging
logging.basicConfig(level = logging.WARNING)

# Register Cogs
bot.add_cog(aki.Aki(bot))
bot.add_cog(bigmoji.Bigmoji(bot))
# bot.add_cog(birthday.Birthday())
bot.add_cog(botstatus.Botstatus(bot))
bot.add_cog(comics.Comics(bot))
bot.add_cog(connect4.Connect4(bot))
bot.add_cog(conversationgames.ConversationGames())
bot.add_cog(core.Core(bot))
bot.add_cog(covid.Covid(bot))
bot.add_cog(fun.Fun(bot))
bot.add_cog(hangman.Hangman(bot))
# bot.add_cog(ipl.IPL(bot))
bot.add_cog(math.Math(bot))
bot.add_cog(meme.Meme())
bot.add_cog(moderation.Mod(bot))
bot.add_cog(music.Music(bot))
bot.add_cog(photo.Photo())
bot.add_cog(starboard.Starboard(bot))
bot.add_cog(qtopia.Qtopia(bot))
bot.add_cog(quiz.Quiz(bot))
bot.add_cog(tictactoe.TTT(bot))
bot.add_cog(timezone.Timezone())

# Start scheduled commands
scheduler = schedule_jobs.Scheduler(bot).schedule()
scheduler.start()

# Run the bot
bot.run(BOT_TOKEN)