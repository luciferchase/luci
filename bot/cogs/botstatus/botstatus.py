import discord
from discord.ext import commands

import logging
import os
import psycopg2


class Botstatus(commands.Cog):
    """Set up status of bot"""
    def __init__(self, bot):
        self.bot = bot

        # Set up database
        DATABASE_URL = os.environ["DATABASE_URL"]

        self.dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
        self.cursor = self.dbcon.cursor()

        query = """CREATE TABLE IF NOT EXISTS botstatus(
                status      TEXT    NOT NULL,
                activity    TEXT,
                name        TEXT)"""
        self.cursor.execute(query)
        self.dbcon.commit()

    async def set_botstatus_on_ready(self):
        # Change botstatus from datatbase
        try:
            self.cursor.execute("SELECT * FROM botstatus")
            data = self.cursor.fetchall()
        except:
            data = []

        if (len(data) != 0):
            data = data[0]

            status_class = {
                "o": discord.Status.online,
                "i": discord.Status.idle,
                "d": discord.Status.dnd
            }

            activity_type = {
                "p": discord.Game(name = data[2]),
                "l": discord.Activity(type = discord.ActivityType.listening, name = data[2]),
                "w": discord.Activity(type = discord.ActivityType.watching, name = data[2]),
                "c": discord.Activity(type = discord.ActivityType.competing, name = data[2])
            }

        # Default status
        else:
            status_class = discord.Status.idle
            activity_type = discord.Activity(type = discord.ActivityType.watching, name = "your cute smile")

        try:
            await self.bot.change_presence(status = status_class[data[0]], activity = activity_type[data[1]])
            print("Activity set successfully")
        except Exception as e:
            await ctx.send(f"```css\n{e}```")

    @commands.is_owner()
    @commands.command(hidden = True, aliases = ["status", "bs"])
    async def botstatus(self, ctx, *query):
        """Set botstatus `luci <status> <activity> <text>`
        `status` can be: online[o], idle[i], dnd[d]
        `activity` can be : playing[p], listening[l], watching[w], competing[c]
        """
        status, activity, *text = query
        text = " ".join(text)

        self.cursor.execute("DELETE FROM botstatus")
        self.dbcon.commit()

        try:
            query = f"""INSERT INTO botstatus VALUES
                    ('{status}', '{activity}', '{text}')"""
            self.cursor.execute(query)
            self.dbcon.commit()
        except Exception as e:
            await ctx.send("Cannot add it status to database. Check logs.")
            await ctx.send(f"```css\n{e}```")

        status_class = {
            "o": discord.Status.online,
            "i": discord.Status.idle,
            "d": discord.Status.dnd
        }

        activity_type = {
            "p": discord.Game(name = text),
            "l": discord.Activity(type = discord.ActivityType.listening, name = text),
            "w": discord.Activity(type = discord.ActivityType.watching, name = text),
            "c": discord.Activity(type = discord.ActivityType.competing, name = text)
        }

        try:
            await self.bot.change_presence(status = status_class[status], activity = activity_type[activity])
            await ctx.send("Activity set successfully")
        except Exception as e:
            await ctx.send(f"```css\n{e}```")
            await ctx.send("Cannot set activity")

