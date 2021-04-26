# Install all dependencies
import discord
from discord.ext import commands

import os
import logging

# Configure the bot
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = commands.Bot(command_prefix = "luci ")

# Commands
@bot.event
async def on_ready() :
	await bot.change_presence(
		status = discord.Status.idle, 
		activity = discord.CustomActivity("Always with you")
	)
	print("")

@bot.command()
async def ping(ctx) :
	await ctx.send(f"🏓 Pong with {str(round(bot.latency, 2))}")
