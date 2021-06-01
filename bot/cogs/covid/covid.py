import discord
from discord.ext import commands

import aiohttp
from babel.numbers import format_decimal
import datetime
import typing
from typing import Union
import os

from .menus import ArticleFormat, CovidMenu, CovidStateMenu, GenericMenu


class Covid(commands.Cog):
    """Covid-19 (Novel Coronavirus Stats)."""

    def __init__(self, bot):
        self.bot = bot
        self.api = "https://disease.sh/v3/covid-19"
        self.newsapi = "https://newsapi.org/v2/top-headlines"
        self.params = {
            "q": "COVID",
            "sortBy": "publishedAt",
            "pageSize": 100,
            "country": None,
            "apiKey": os.getenv("NEWS_API_KEY"),
            "page": 1
        }
        self.session = aiohttp.ClientSession()
        self.newsapikey = None

    def humanize_number(self, val: Union[int, float]) -> str:
        """
        Convert an int or float to a str with digit separators based on bot locale

        Parameters
        ----------
        val : Union[int, float]
            The int/float to be formatted.
        override_locale: Optional[str]
            A value to override bot's regional format.

        Returns
        -------
        str
            locale aware formatted number.
        """
        return format_decimal(val)

    async def get(self, url, params):
        async with self.session.get(url, params = params) as response:
            try:
                data = await response.json()
            except aiohttp.ContentTypeError:
                return {
                    "failed": "Their appears to be an issue with the API. Please try again later."
                }
            
            if response.status == 200:
                try:
                    if isinstance(data, dict) and data.get("message") is not None:
                        return {"failed": data["message"]}
                    return data
                except aiohttp.ServerTimeoutError:
                    return {
                        "failed": "Their appears to be an issue with the API. Please try again later."
                    }
            else:
                return {"failed": data["message"]}

    @commands.command(hidden = True)
    async def covidcountries(self, ctx):
        """Countries supported by covidnews."""
        
        country_codes = str("ae ar at au be bg br ca ch cn co cu cz de eg fr gb gr hk" + 
        " hu id ie il in it jp kr lt lv ma mx my ng nl no nz ph pl pt ro rs ru sa se sg" + 
        " si sk th tr tw ua us ve za").split()

        await ctx.send("```css\nValid County Codes are:\n{}```".format("\n".join(country_codes)))

    @commands.command()
    @commands.bot_has_permissions(embed_links = True)
    async def covidnews(self, ctx, countrycode: str):
        """Covid News from a Country - County must be 2-letter ISO 3166-1 code.

        Check luci covidcountries for a list of all possible country codes supported."""

        self.params["country"] = countrycode
        
        async with ctx.typing():
            data = await self.get(self.newsapi, params = self.params)

        if data.get("failed") is not None:
            return await ctx.send(data.get("failed"))
        
        if data["totalResults"] == 0:
            await ctx.send("No results found, ensure you're looking up the correct country code.")
            await ctx.send("Check luci covidcountries for a list.")
            return
        
        await GenericMenu(source = ArticleFormat(data["articles"]), ctx = ctx,).start(
            ctx = ctx,
            wait = False,
        )

    @commands.group(invoke_without_command = True)
    @commands.bot_has_permissions(embed_links = True)
    async def covid(self, ctx, *, country: typing.Optional[str]):
        """Stats about Covid-19 or countries if provided.

        Supports multiple countries seperated by a comma.
        Example: luci covid Ireland, England
        """

        if not country:
            async with ctx.typing():
                data = await self.get(self.api + "/all")
            
            if isinstance(data, dict) and data.get("failed") is not None:
                return await ctx.send(data.get("failed"))
            if not data:
                return await ctx.send("No data available.")
            
            embed = discord.Embed(
                color = await self.bot.get_embed_color(ctx.channel),
                title= "Covid-19 Global Statistics",
                timestamp = datetime.datetime.utcfromtimestamp(data["updated"] / 1000),
            )
            embed.add_field(name = "Cases", value = self.humanize_number(data["cases"]))
            embed.add_field(name = "Deaths", value = self.humanize_number(data["deaths"]))
            embed.add_field(name = "Recovered", value = self.humanize_number(data["recovered"]))
            embed.add_field(name = "Critical", value = self.humanize_number(data["critical"]))
            embed.add_field(name = "Active", value = self.humanize_number(data["active"]))
            embed.add_field(
                name = "Affected Countries", value = self.humanize_number(data["affectedCountries"])
            )
            embed.add_field(name = "Cases Today", value = self.humanize_number(data["todayCases"]))
            embed.add_field(name = "Deaths Today", value = self.humanize_number(data["todayDeaths"]))
            embed.add_field(name = "Recovered Today", value = self.humanize_number(data["todayRecovered"]))
            embed.add_field(name = "Total Tests", value = self.humanize_number(data["tests"]))
            
            await ctx.send(embed = embed)
        else:
            async with ctx.typing():
                data = await self.get(self.api + "/countries/{}".format(country))
            
            if isinstance(data, dict):
                error = data.get("failed")
                if error is not None:
                    return await ctx.send(error)
                data = [data]
            if not data:
                return await ctx.send("No data available.")
            
            await GenericMenu(source = CovidMenu(data), ctx = ctx, type= "Today").start(
                ctx = ctx,
                wait = False,
            )

    @covid.command()
    @commands.bot_has_permissions(embed_links = True)
    async def yesterday(self, ctx, *, country: str):
        """Show the statistics from yesterday for countries.

        Supports multiple countries seperated by a comma.
        Example: luci covid yesterday Ireland, England
        """
        async with ctx.typing():
            data = await self.get(self.api + "/countries/{}?yesterday = 1".format(country))
            if isinstance(data, dict):
                error = data.get("failed")
                if error is not None:
                    return await ctx.send(error)
                data = [data]
            if not data:
                return await ctx.send("No data available.")
            
            await GenericMenu(source = CovidMenu(data), ctx = ctx, type= "Yesterday").start(
                ctx = ctx,
                wait = False,
            )

    @covid.command()
    @commands.bot_has_permissions(embed_links = True)
    async def todaycases(self, ctx):
        """Show the highest cases from countrys today."""
        async with ctx.typing():
            data = await self.get(self.api + "/countries?sort = todayCases")
            
            if isinstance(data, dict):
                error = data.get("failed")
                if error is not None:
                    return await ctx.send(error)
            if not data:
                return await ctx.send("No data available.")
            
            embed = discord.Embed(
                color = await self.bot.get_embed_color(ctx.channel),
                title= "Covid-19 | Highest Cases Today | {}".format(data[0]["country"]),
                timestamp = datetime.datetime.utcfromtimestamp(data[0]["updated"] / 1000),
            )
            embed.add_field(name = "Cases", value = self.humanize_number(data[0]["cases"]))
            embed.add_field(name = "Deaths", value = self.humanize_number(data[0]["deaths"]))
            embed.add_field(name = "Recovered", value = self.humanize_number(data[0]["recovered"]))
            embed.add_field(name = "Cases Today", value = self.humanize_number(data[0]["todayCases"]))
            embed.add_field(name = "Deaths Today", value = self.humanize_number(data[0]["todayDeaths"]))
            embed.add_field(name = "Critical Condition", value = self.humanize_number(data[0]["critical"]))
            
            await ctx.send(embed = embed)

    @covid.command()
    @commands.bot_has_permissions(embed_links = True)
    async def todaydeaths(self, ctx):
        """Show the highest deaths from countrys today."""
        async with ctx.typing():
            data = await self.get(self.api + "/countries?sort = todayDeaths")
            
            if isinstance(data, dict):
                error = data.get("failed")
                if error is not None:
                    return await ctx.send(error)
            if not data:
                return await ctx.send("No data available.")
            
            embed = discord.Embed(
                color = await self.bot.get_embed_color(ctx.channel),
                title= "Covid-19 | Highest Deaths Today | {}".format(data[0]["country"]),
                timestamp = datetime.datetime.utcfromtimestamp(data[0]["updated"] / 1000),
            )
            embed.add_field(name = "Cases", value = self.humanize_number(data[0]["cases"]))
            embed.add_field(name = "Deaths", value = self.humanize_number(data[0]["deaths"]))
            embed.add_field(name = "Recovered", value = self.humanize_number(data[0]["recovered"]))
            embed.add_field(name = "Cases Today", value = self.humanize_number(data[0]["todayCases"]))
            embed.add_field(name = "Deaths Today", value = self.humanize_number(data[0]["todayDeaths"]))
            embed.add_field(name = "Critical Condition", value = self.humanize_number(data[0]["critical"]))
           
            await ctx.send(embed = embed)

    @covid.command()
    @commands.bot_has_permissions(embed_links = True)
    async def highestcases(self, ctx):
        """Show the highest cases from countrys overall."""
        async with ctx.typing():
            data = await self.get(self.api + "/countries?sort = cases")
            
            if isinstance(data, dict):
                error = data.get("failed")
                if error is not None:
                    return await ctx.send(error)
            if not data:
                return await ctx.send("No data available.")
            
            embed = discord.Embed(
                color = await self.bot.get_embed_color(ctx.channel),
                title= "Covid-19 | Highest Cases Overall | {}".format(data[0]["country"]),
                timestamp = datetime.datetime.utcfromtimestamp(data[0]["updated"] / 1000),
            )
            embed.add_field(name = "Cases", value = self.humanize_number(data[0]["cases"]))
            embed.add_field(name = "Deaths", value = self.humanize_number(data[0]["deaths"]))
            embed.add_field(name = "Recovered", value = self.humanize_number(data[0]["recovered"]))
            embed.add_field(name = "Cases Today", value = self.humanize_number(data[0]["todayCases"]))
            embed.add_field(name = "Deaths Today", value = self.humanize_number(data[0]["todayDeaths"]))
            embed.add_field(name = "Critical Condition", value = self.humanize_number(data[0]["critical"]))
            await ctx.send(embed = embed)

    @covid.command()
    @commands.bot_has_permissions(embed_links = True)
    async def highestdeaths(self, ctx):
        """Show the highest deaths from countrys overall."""
        
        async with ctx.typing():
            data = await self.get(self.api + "/countries?sort = deaths")
            
            if isinstance(data, dict):
                error = data.get("failed")
                if error is not None:
                    return await ctx.send(error)
            if not data:
                return await ctx.send("No data available.")
            
            embed = discord.Embed(
                color = await self.bot.get_embed_color(ctx.channel),
                title= "Covid-19 | Highest Deaths Overall | {}".format(data[0]["country"]),
                timestamp = datetime.datetime.utcfromtimestamp(data[0]["updated"] / 1000),
            )
            embed.add_field(name = "Cases", value = self.humanize_number(data[0]["cases"]))
            embed.add_field(name = "Deaths", value = self.humanize_number(data[0]["deaths"]))
            embed.add_field(name = "Recovered", value = self.humanize_number(data[0]["recovered"]))
            embed.add_field(name = "Cases Today", value = self.humanize_number(data[0]["todayCases"]))
            embed.add_field(name = "Deaths Today", value = self.humanize_number(data[0]["todayDeaths"]))
            embed.add_field(name = "Critical Condition", value = self.humanize_number(data[0]["critical"]))
            
            await ctx.send(embed = embed)

    @covid.command()
    @commands.bot_has_permissions(embed_links = True)
    async def topcases(self, ctx, amount: int = 6):
        """Show X countries with top amount of cases.

        Defaults to 6.
        """
        
        if amount > 20 or amount < 0:
            return await ctx.send("Invalid amount. Please choose between an amount between 1-20.")
        
        async with ctx.typing():
            data = await self.get(self.api + "/countries?sort = cases")
            
            if isinstance(data, dict):
                error = data.get("failed")
                if error is not None:
                    return await ctx.send(error)
            if not data:
                return await ctx.send("No data available.")
            
            embed = discord.Embed(
                color = await self.bot.get_embed_color(ctx.channel),
                title= "Covid-19 | Top {} Cases ".format(amount),
                timestamp = datetime.datetime.utcfromtimestamp(data[0]["updated"] / 1000),
            )
            for i in range(amount):
                cases = self.humanize_number(data[i]["cases"])
                deaths = self.humanize_number(data[i]["deaths"])
                recovered = self.humanize_number(data[i]["recovered"])
                todayCases = self.humanize_number(data[i]["todayCases"])
                todayDeaths = self.humanize_number(data[i]["todayDeaths"])
                critical = self.humanize_number(data[i]["critical"])

                msg = str('**Cases**: {}\n**Deaths**: {}\n**Recovered**: {}\n**Cases Today**: {}' + 
                '\n**Deaths Today**: {}\n**Critical**: {}').format(cases, deaths, recovered, 
                todayCases, todayDeaths. critical)

                embed.add_field(name  = data[i]["country"], value = msg)
            
            await ctx.send(embed = embed)

    @covid.command()
    @commands.bot_has_permissions(embed_links = True)
    async def topcasestoday(self, ctx, amount: int = 6):
        """Show X countries with top amount of cases today.

        Defaults to 6.
        """
        
        if amount > 20 or amount < 0:
            return await ctx.send("Invalid amount. Please choose between an amount between 1-20.")
        
        async with ctx.typing():
            data = await self.get(self.api + "/countries?sort = todayCases")
            
            if isinstance(data, dict):
                error = data.get("failed")
                if error is not None:
                    return await ctx.send(error)
            if not data:
                return await ctx.send("No data available.")
            
            embed = discord.Embed(
                color = await self.bot.get_embed_color(ctx.channel),
                title= "Covid-19 | Top {} Cases Today ".format(amount),
                timestamp = datetime.datetime.utcfromtimestamp(data[0]["updated"] / 1000),
            )
            for i in range(amount):
                cases = self.humanize_number(data[i]["cases"])
                deaths = self.humanize_number(data[i]["deaths"])
                recovered = self.humanize_number(data[i]["recovered"])
                todayCases = self.humanize_number(data[i]["todayCases"])
                todayDeaths = self.humanize_number(data[i]["todayDeaths"])
                critical = self.humanize_number(data[i]["critical"])

                msg = str('**Cases**: {}\n**Deaths**: {}\n**Recovered**: {}\n**Cases Today**: {}' + 
                '\n**Deaths Today**: {}\n**Critical**: {}').format(cases, deaths, recovered, 
                todayCases, todayDeaths. critical)
                
                embed.add_field(name  = data[i]["country"], value = msg)
            
            await ctx.send(embed = embed)

    @covid.command()
    @commands.bot_has_permissions(embed_links = True)
    async def topdeaths(self, ctx, amount: int = 6):
        """Show X countries with top amount of deaths.

        Defaults to 6.
        """
        
        if amount > 20 or amount < 0:
            return await ctx.send("Invalid amount. Please choose between an amount between 1-20.")
        
        async with ctx.typing():
            data = await self.get(self.api + "/countries?sort = deaths")
            
            if isinstance(data, dict):
                error = data.get("failed")
                if error is not None:
                    return await ctx.send(error)
            if not data:
                return await ctx.send("No data available.")
            
            embed = discord.Embed(
                color = await self.bot.get_embed_color(ctx.channel),
                title= "Covid-19 | Top {} Deaths ".format(amount),
                timestamp = datetime.datetime.utcfromtimestamp(data[0]["updated"] / 1000),
            )
            for i in range(amount):
                cases = self.humanize_number(data[i]["cases"])
                deaths = self.humanize_number(data[i]["deaths"])
                recovered = self.humanize_number(data[i]["recovered"])
                todayCases = self.humanize_number(data[i]["todayCases"])
                todayDeaths = self.humanize_number(data[i]["todayDeaths"])
                critical = self.humanize_number(data[i]["critical"])

                msg = str('**Cases**: {}\n**Deaths**: {}\n**Recovered**: {}\n**Cases Today**: {}' + 
                '\n**Deaths Today**: {}\n**Critical**: {}').format(cases, deaths, recovered, 
                todayCases, todayDeaths. critical)

                embed.add_field(name  = data[i]["country"], value = msg)
           
            await ctx.send(embed = embed)

    @covid.command()
    @commands.bot_has_permissions(embed_links = True)
    async def topdeathstoday(self, ctx, amount: int = 6):
        """Show X countries with top amount of deaths today.

        Defaults to 6.
        """
        
        if amount > 20 or amount < 0:
            return await ctx.send("Invalid amount. Please choose between an amount between 1-20.")
        
        async with ctx.typing():
            data = await self.get(self.api + "/countries?sort = todayDeaths")
            
            if isinstance(data, dict):
                error = data.get("failed")
                if error is not None:
                    return await ctx.send(error)
            if not data:
                return await ctx.send("No data available.")
            
            embed = discord.Embed(
                color = await self.bot.get_embed_color(ctx.channel),
                title= "Covid-19 | Top {} Deaths Today ".format(amount),
                timestamp = datetime.datetime.utcfromtimestamp(data[0]["updated"] / 1000),
            )
            for i in range(amount):
                cases = self.humanize_number(data[i]["cases"])
                deaths = self.humanize_number(data[i]["deaths"])
                recovered = self.humanize_number(data[i]["recovered"])
                todayCases = self.humanize_number(data[i]["todayCases"])
                todayDeaths = self.humanize_number(data[i]["todayDeaths"])
                critical = self.humanize_number(data[i]["critical"])

                msg = str('**Cases**: {}\n**Deaths**: {}\n**Recovered**: {}\n**Cases Today**: {}' + 
                '\n**Deaths Today**: {}\n**Critical**: {}').format(cases, deaths, recovered, 
                todayCases, todayDeaths. critical)
                
                embed.add_field(name  = data[i]["country"], value = msg)
            
            await ctx.send(embed = embed)

    @covid.group(invoke_without_command = True)
    @commands.bot_has_permissions(embed_links = True)
    async def state(self, ctx, *, states: str):
        """Show stats for specific states.

        Supports multiple countries seperated by a comma.
        Example: luci covid state New York, California
        """
        
        if not states:
            return await ctx.send_help()
        
        async with ctx.typing():
            states = ",".join(states.split(", "))
            data = await self.get(self.api + "/states/{}".format(states))
            
            if isinstance(data, dict):
                error = data.get("failed")
                if error is not None:
                    return await ctx.send(error)
                data = [data]
            if not data:
                return await ctx.send("No data available.")
            
            await GenericMenu(source = CovidStateMenu(data), ctx = ctx, type= "Today").start(
                ctx = ctx,
                wait = False,
            )

    @state.command(name = "yesterday")
    @commands.bot_has_permissions(embed_links = True)
    async def _yesterday(self, ctx, *, states: str):
        """Show stats for yesterday for specific states.

        Supports multiple countries seperated by a comma.
        Example: luci covid state yesterday New York, California.
        """
        
        async with ctx.typing():
            states = ",".join(states.split(", "))
            data = await self.get(self.api + "/states/{}?yesterday = 1".format(states))
            
            if isinstance(data, dict):
                error = data.get("failed")
                if error is not None:
                    return await ctx.send(error)
                data = [data]
            if not data:
                return await ctx.send("No data available.")
            
            await GenericMenu(source = CovidStateMenu(data), ctx = ctx, type= "Yesterday").start(
                ctx = ctx,
                wait = False,
            )
