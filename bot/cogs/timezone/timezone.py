import discord
from discord.ext import commands

from datetime import datetime
import pytz


class Timezone(commands.Cog):
    """Convert local time to different timezones"""

    @commands.command(aliases = ["tz"])
    async def time(self, ctx, *, country = None):
        """Example: luci tz london"""

        if (not country):
            country = "UTC"
        if (country.lower() == "usa"):
            country = "america"

        country = "_".join(country)
        list_of_timezones = list(pytz.all_timezones)
        
        for i in range(len(list_of_timezones)):
            if (country.title() in list_of_timezones[i]):
                country = list_of_timezones[i]
                found_timezones.append(country)
        else:
            await ctx.send("Uh oh! No country found 👀")
            await ctx.send("You can check list of accepted timezones using `luci timezones [continent name]`")
            return

        # Current time in UTC
        now_utc = datetime.now(pytz.timezone("UTC"))

        # Convert it to appropriate timezone
        different_tz = now_utc.astimezone(pytz.timezone(country))
        await ctx.send("```css\n{}: {}```".format(country, different_tz.strftime('%H:%M')))

    @commands.command()
    async def timezones(self, ctx, *continent):
        continent = "_".join(continent)
        tz_list = []

        for tz in list(pytz.all_timezones):
            if (continent.title() in tz):
                tz_list.append(tz)
        else:
            await ctx.send(f'Bruh! Are you sure {" ".join(continent.split("_")).title()} is a continent? 🤦‍♂️')
            return

        await ctx.send("```css\n{}```".format('\n'.join(tz_list)))