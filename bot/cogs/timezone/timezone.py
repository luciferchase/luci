import discord
from discord.ext import commands

from datetime import datetime, timedelta
import pytz


class Timezone(commands.Cog):
    """Convert local time to different timezones"""
    def __init__(self):
        self.fmt = "%H:%M"

    @commands.command(aliases = ["tz"])
    async def time(self, ctx, *country):
        """Example: luci time london"""

        country = "_".join(country)

        if (country.lower() == "usa"):
            country = "america"

        list_of_timezones = list(pytz.all_timezones)
        
        for i in range(len(list_of_timezones)):
            if (country.title() in list_of_timezones[i]):
                country = list_of_timezones[i]
                break
        else:
            await ctx.send("Uh oh! Timezone not found 👀")
            await ctx.send("You can check list of timezones using `luci timezones [continent name]`")
            return

        # Current time in UTC
        now_utc = datetime.now(pytz.timezone("UTC"))

        # Convert it to appropriate timezone
        different_tz = now_utc.astimezone(pytz.timezone(country))
        await ctx.send("```css\n{}: {}```".format(country, different_tz.strftime(self.fmt)))

    @commands.command()
    async def convert(self, ctx, tz_1, tz_2, *timestamp):
        """Example: luci convert london kolkata 12:56"""

        timestamp = timestamp[0]
        if (":" not in timestamp):
            timestamp += ":00"
        if (len(timestamp.split(":")[0]) == 1):
            timestamp = "0" + timestamp

        # Convert timestamp to datetime object
        timestamp = datetime.strptime(timestamp, "%H:%M")
        
        if (tz_1.lower() == "usa"):
            tz_1 = "america"
        if (tz_2.lower() == "usa"):
            tz_2 = "america"

        list_of_timezones = list(pytz.all_timezones)

        found_1, found_2 = (False, False)
        
        for i in range(len(list_of_timezones)):
            if (found_1 and found_2):
                break

            if (tz_1.title() in list_of_timezones[i]):
                tz_1 = list_of_timezones[i]
                found_1 = True
            elif (tz_2.title() in list_of_timezones[i]):
                tz_2 = list_of_timezones[i]
                found_2 = True

        else:
            if (not found_1):
                country_not_found = "first timezone"
            elif (not found_2):
                country_not_found = "second timezone"
            else:
                country_not_found = "both the timezone"

            await ctx.send(f"Uh oh! Your {country_not_found} not found 👀")
            await ctx.send("You can check list of timezones using `luci timezones [continent name]`")
            return
        
        # First we will get the time difference between the timezones
        # Current time in UTC
        now_utc = datetime.now(pytz.timezone("UTC"))

        time_in_tz1 = now_utc.astimezone(pytz.timezone(tz_1))
        time_in_tz2 = now_utc.astimezone(pytz.timezone(tz_2))

        difference_in_time = time_in_tz2 - time_in_tz1

        await ctx.send("```css\n{}: {}\n{}: {}```".format(
            tz_1, timestamp.strftime(self.fmt), tz_2, (timestamp + difference_in_time).strftime(self.fmt)))

    @commands.command()
    async def timezones(self, ctx, *continent):
        """See list of accepted timezones"""
        continent = "_".join(continent)
        tz_list = []

        for tz in list(pytz.all_timezones):
            if (continent.title() in tz):
                tz_list.append(tz)
        
        if ((len(tz_list)) == 0):
            await ctx.send(f'Bruh! Are you sure {" ".join(continent.split("_")).title()} is a continent? 🤦‍♂️')
            return

        try:
            await ctx.send("```css\n{}```".format('\n'.join(tz_list)))
        except:
            await ctx.send("```css\n{}```".format('\n'.join(tz_list[30:])))
            await ctx.send("```css\n{}```".format('\n'.join(tz_list[:30])))