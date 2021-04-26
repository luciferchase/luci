# Install all dependencies
import discord
from discord.ext import commands

import os
from dotenv import load_dotenv
import logging

# Configure the bot
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = commands.Bot(command_prefix = "luci ")

# Main Commands
@bot.event
async def on_ready() :
	await bot.change_presence(status = discord.Status.idle, activity = discord.Game("Listening to .help"))
	print("I am online")

@bot.command()
async def ping(ctx) :
	await ctx.send(f"🏓 Pong with {str(round(bot.latency, 2))}")

bot.run(BOT_TOKEN)
