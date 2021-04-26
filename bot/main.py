# Install all dependencies
import discord
from discord.ext import commands

import os
import logging

# Configure the bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = commands.Bot(command_prefix = "luci ")

class Bot(bot):
	
	def __init__(self, bot):
		self._shutdown_mode = ExitCodes.CRITICAL

	async def shutdown(self, *, restart: bool = False):
		"""Gracefully quit Red.

		The program will exit with code :code:`0` by default.

		Parameters
		----------
		restart : bool
			If :code:`True`, the program will exit with code :code:`26`. If the
			launcher sees this, it will attempt to restart the bot.

		"""
		if not restart:
			self._shutdown_mode = ExitCodes.SHUTDOWN
		else:
			self._shutdown_mode = ExitCodes.RESTART

		await self.close()
		sys.exit(self._shutdown_mode)
	


# Commands
@bot.event
async def on_ready() :
	await bot.change_presence(status = discord.Status.idle, activity = discord.Game("Always with you"))
	print("")

@bot.command()
async def ping(ctx) :
	await ctx.send(f"🏓 Pong with {str(round(bot.latency, 2))}")


class ExitCodes(IntEnum):
	# This needs to be an int enum to be used
	# with sys.exit
	CRITICAL = 1
	SHUTDOWN = 0
	RESTART = 2

bot.run(BOT_TOKEN)

