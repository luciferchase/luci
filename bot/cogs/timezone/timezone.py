import discord
from discord.ext import commands

import pytz


class Timezone(commands.Cog):
    """Convert local time to different timezones"""

    @commands.command(aliases = ["tz", "timezone"])
    async def time(self, ctx, country, *, time = None):
        """Example: luci tz america 12:56"""

        if (country.lower() == "usa"):
            country = "america"

        list_of_timezones = pytz.all_timezones
        
        for i in range(len(list_of_timezones)):
            if (country.title() in list_of_timezones[i]):
                country = list_of_timezones[i]
                break
        else:
            await ctx.send("Uh oh! No country found 👀")
            await ctx.send("You can check list of accepted countries [here](http://en.wikipedia.org/wiki/List_of_tz_database_time_zones)")

        if not time:
            time = datetime.now(timezone(country)).strftime("%H:%M")
            await ctx.send(time)