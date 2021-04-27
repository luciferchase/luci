import akinator
from akinator.async_aki import Akinator

import discord
from discord.ext import commands

import logging
import cogs.core.menus as menus


class AkiMenu(menus.Menu):
	def __init__(self, game = Akinator, color = 0xf34949):
		self.aki = game
		self.color = color
		self.num = 1
		self.message = None
		super().__init__(timeout = 60, delete_message_after = False, clear_reactions_after = True)

	async def send_initial_message(self, ctx: commands.Context, channel: discord.TextChannel):
		return await channel.send(embed = self.current_question_embed())

	@menus.button("✅")
	async def yes(self, payload: discord.RawReactionActionEvent):
		self.num += 1
		await self.answer("yes")
		await self.send_current_question()

	@menus.button("❎")
	async def no(self, payload: discord.RawReactionActionEvent):
		self.num += 1
		await self.answer("no")
		await self.send_current_question()

	@menus.button("❔")
	async def idk(self, payload: discord.RawReactionActionEvent):
		self.num += 1
		await self.answer("idk")
		await self.send_current_question()

	@menus.button("🤔")
	async def probably(self, payload: discord.RawReactionActionEvent):
		self.num += 1
		await self.answer("probably")
		await self.send_current_question()

	@menus.button("🤷‍♂️")
	async def probably_not(self, payload: discord.RawReactionActionEvent):
		self.num += 1
		await self.answer("probably not")
		await self.send_current_question()

	@menus.button("◀️")
	async def back(self, payload: discord.RawReactionActionEvent):
		try:
			await self.aki.back()
		except akinator.CantGoBackAnyFurther:
			await self.ctx.send(
				"You can't go back on the first question, try a different option instead.",
				delete_after=10,
			)
		else:
			self.num -= 1
			await self.send_current_question()

	@menus.button("🏆")
	async def react_win(self, payload: discord.RawReactionActionEvent):
		await self.win()

	@menus.button("🗑️")
	async def end(self, payload: discord.RawReactionActionEvent):
		await self.cancel()

	def current_question_embed(self):
		embed = discord.Embed(
			color = self.color,
			title = f"Question #{self.num}",
			description = self.aki.question,
		)
		if self.aki.progression > 0:
			embed.set_footer(text = f"{round(self.aki.progression, 2)}% guessed")
		return embed

	async def win(self):
		winner = await self.aki.win()
		win_embed = discord.Embed(
			color=self.color,
			title=f"I'm {round(float(winner['proba']) * 100)}% sure it's {winner['name']}!",
			description=winner["description"],
		)
		win_embed.set_image(url=winner["absolute_picture_path"])
		await self.edit_or_send(embed=win_embed)
		self.stop()
		# TODO allow for continuation of game

	async def send_current_question(self):
		if self.aki.progression < 80:
			try:
				await self.message.edit(embed=self.current_question_embed())
			except discord.HTTPException:
				await self.cancel()
		else:
			await self.win()

	async def finalize(self, timed_out: bool):
		if timed_out:
			await self.edit_or_send(content="Akinator game timed out.", embed=None)

	async def cancel(self):
		await self.edit_or_send(content="Akinator game cancelled.", embed=None)
		self.stop()

	async def edit_or_send(self, **kwargs):
		try:
			await self.message.edit(**kwargs)
		except discord.NotFound:
			await self.ctx.send(**kwargs)
		except discord.Forbidden:
			pass

	async def answer(self, message: str):
		try:
			await self.aki.answer(message)
		except akinator.AkiNoQuestions:
			await self.win()
		except Exception as error:
			log.exception(
				f"Encountered an exception while answering with {message} during Akinator session",
				exc_info=True,
			)
			await self.edit_or_send(content=f"Akinator game errored out:\n`{error}`", embed=None)
			self.stop()


class Aki(commands.Cog):
	"""
	Play Akinator in Discord!
	"""

	def __init__(self, bot) -> None:
		self.bot = bot

	@commands.max_concurrency(1, commands.BucketType.channel)
	@commands.bot_has_permissions(embed_links=True, add_reactions=True)
	@commands.command()
	async def aki(self, ctx: commands.Context, *, language: str.lower = "en"):
		"""
		Start a game of Akinator!

		Controls:
		> ✅ : yes
		> ❎ : no
		> ❔ : i don't know
		> 🤔 : probably
		> 🤷‍♂️ : probably not
		> ◀️ : back
		> 🏆 : win
		> 🗑️ : cancel
		"""
		
		# Send emoji info
		embed = discord.Embed(
			title = "Akinator",
			description = "*Controls*:\n \
			✅ : yes \n \
			❎ : no \n \
			❔ : i don't know \n \
			🤔 : probably \n \
			🤷‍♂️ : probably not \n \
			◀️ : back \n \
			🏆 : win \n \
			🗑️ : cancel",
			color = 0xf34949
		)
		await ctx.send(embed = embed, delete_after = 20)

		await ctx.trigger_typing()
		aki = Akinator()
		try:
			await aki.start_game(language=language.replace(" ", "_"))
		except akinator.InvalidLanguageError:
			await ctx.send(
				"Invalid language. Refer here to view valid languages.\
				\n<https://github.com/NinjaSnail1080/akinator.py#functions>"
			)
		except Exception:
			await ctx.send("I encountered an error while connecting to the Akinator servers.")
		else:
			menu = AkiMenu(aki)
			await menu.start(ctx)
