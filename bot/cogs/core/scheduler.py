import discord
from discord.ext import tasks, commands

from cogs.meme.meme import Meme

class Scheduler(commands.Cog):
	"""Schedule vairous commands"""

	def __init__(self):
		# Run Schdelued Tasks
		print("Running Scheduled Tasks")
		self.scheduled.start()

	# Scheduled tasks
	@tasks.loop(seconds = 30)
	async def scheduled(self):
		Meme.meme()

	@scheduled.before_loop
	async def before_printer(self):
		print('waiting...')
		await self.bot.wait_until_ready()
