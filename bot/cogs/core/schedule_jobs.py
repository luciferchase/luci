import discord
from discord.ext import commands

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import aiohttp
from datetime import datetime, date, time
import logging
import os
import psycopg2
import pytz

from cogs.ipl import ipl

class Scheduler(commands.Cog):
    """Schedule commands."""
    def __init__(self, bot):
        self.bot = bot

        # Initialize session
        self.session = aiohttp.ClientSession()
    
    # Scheduled events
    async def schedule_meme(self):
        config = {
            "qtopia": [587164191710773268, True],
            "aech": [835113922172026881, True]
        }
        
        async with self.session.get("https://meme-api.herokuapp.com/gimme/dankmemes") as response:
            data = await response.json()

            for channel_id in config.values():
                if (not channel_id[1]):
                    return

                channel = self.bot.get_channel(channel_id[0])

                embed = discord.Embed(
                    color = 0x06f9f5,                           # Blue-ish
                    title = data["title"],
                    url = data["postLink"]
                )
                embed.set_image(url = data["url"])
                embed.set_footer(text = f'👍 {data["ups"]}')
                meme = await channel.send(embed = embed)
                await meme.add_reaction("😂")
                await meme.add_reaction("leo-1:748517015962255440")

    async def schedule_wallpaper(self):
        config = {
            "qtopia": [587156041716727848, True],
            "aech": [738731755569414197, True]
        }

        api = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1&mkt=en-US"

        async with self.session.get(api) as response:
            data = await response.json()

            for channel_id in config.values():
                if (not channel_id[1]):
                    return

                channel = self.bot.get_channel(channel_id[0])

                await channel.send(data["images"][0]["title"])
                
                wallpaper = await channel.send(f'http://bing.com{data["images"][0]["url"]}')
                await wallpaper.add_reaction("❤️")
                await wallpaper.add_reaction("👍")
                await wallpaper.add_reaction("👎")

    async def schedule_ipl(self):
        # Set up database
        DATABASE_URL = os.environ["DATABASE_URL"]

        dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
        cursor = dbcon.cursor()

        # Get Channel
        channel = self.bot.get_channel(756701639544668160)
        IPL = ipl.IPL(self.bot)

        # Update points and display last winners
        embed = await IPL.show_points()
        await channel.send(embed = embed)

        # Show current standings
        embed = await IPL.fetch_standings()
        await channel.send(embed = embed)

        # Make polls for todays match
        *_, next_match_details, next_match_details_2 = IPL.fetch_matches()

        channel = self.bot.get_channel(756701639544668160)

        allowed_mentions = discord.AllowedMentions(everyone = True)
        await channel.send(content = "@everyone", allowed_mentions = allowed_mentions)

        embed_id = await IPL.predict_code(next_match_details)

        # Update database
        cursor.execute("DELETE FROM predict")
        query = """INSERT INTO predict VALUES
                ({})""".format(embed_id)
        cursor.execute(query)
        dbcon.commit()

        # If there is a second match on that day
        if (next_match_details_2 != False):
            embed_id = await IPL.predict_code(next_match_details_2)

            # Update database
            query = """INSERT INTO predict VALUES
                    ({})""".format(embed_id)
            cursor.execute(query)
            dbcon.commit()

    async def remind_bday(self, data):
        if (data[1] == 587139618999369739):
            channel = await self.bot.fetch_channel(640253357684162561)
        elif (data[1] == 738731754885480468):
            channel = await self.bot.fetch_channel(738731755342790673)
        
        member = await self.bot.fetch_user(data[0])
        await channel.send(f"{member.mention} Happy Birthday! <a:nacho:839499460874862655>") 


    def schedule(self):
        # Initialize scheduler
        schedule_log = logging.getLogger("apscheduler")
        schedule_log.setLevel(logging.WARNING)

        job_defaults = {
            "coalesce": True,  # Multiple missed triggers within the grace time will only fire once
            "max_instances": 5,  # This is probably way too high, should likely only be one
            "misfire_grace_time": 15,  # 15 seconds ain't much, but it's honest work
            "replace_existing": True,  # Very important for persistent data
        }

        scheduler = AsyncIOScheduler(job_defaults = job_defaults, logger = schedule_log)

        # Add jobs to scheduler
        scheduler.add_job(self.schedule_meme, CronTrigger.from_crontab("30 * * * *")) # Every hour

        # Because we are 05:30 hrs ahead of GMT, every cron is set 05:30 hrs behind
        scheduler.add_job(self.schedule_wallpaper, CronTrigger.from_crontab("30 02 * * *")) 
        # Each day at 0800 hrs
        # scheduler.add_job(self.schedule_ipl, CronTrigger.from_crontab("30 02 * * *"))

        # Bday
        # Set up database
        # DATABASE_URL = os.environ["DATABASE_URL"]

        # dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
        # cursor = dbcon.cursor()

        # cursor.execute("SELECT * FROM bday")
        # data = cursor.fetchall()

        # for i in data:
        #     tz_og = pytz.timezone(i[4])
        #     bday = date(datetime.now().year, i[3], i[2])

        #     midnight = tz_og.localize(datetime.combine(bday, time()))
        #     midnight_in_utc = midnight.astimezone(pytz.utc).strftime("%H:%M").split(":")

        #     scheduler.add_job(
        #         lambda: self.remind_bday(i), 
        #         CronTrigger.from_crontab(f"{midnight_in_utc[1]} {midnight_in_utc[0]} {i[2]} {i[3]} *")
        #     )
        # # Start the scheduler
        return scheduler
