import discord
from discord.ext import commands

import json
import os
import psycopg2
import pytz


class Birthday(commands.Cog):
    """Never forget birthday of your friends"""

    def __init__(self):
        # Set up database
        DATABASE_URL = os.environ["DATABASE_URL"]

        self.dbcon = psycopg2.connect(DATABASE_URL, sslmode = "require")
        self.cursor = self.dbcon.cursor()

        # Make a table if not already made
        query = """CREATE TABLE IF NOT EXISTS bday(
                id          BIGINT  NOT NULL    PRIMARY KEY,
                guild_id    BIGINT  NOT NULL,
                bday_date   INT     NOT NULL,
                bday_month  INT     NOT NULL,
                tz          TEXT    NOT NULL
                )"""
        self.cursor.execute(query)
        self.dbcon.commit()

    @commands.guild_only()
    @commands.group(invoke_without_command = True)
    async def bday(self, ctx):
        """To set your bday type `luci bday set`
        If you want to edit a bday type `luci bday edit`"""
        pass

    @bday.command(name = "set")
    async def setbday(self, ctx, member: discord.Member, date, tz = "UTC"):
        """Usage: luci bday set @Lucifer Chase 27/02 kolkata
        If you don't care about the timezone thing leave it blank"""

        date = date.split("/")
        for i in range(2):
            if (date[i][0] == 0):
                date[i] = date[i][1]

        correct_date = True
        if (date[0] > 31 or date[0] < 0 or date[1] > 12 or date[0] < 0):
            correct_date = False

        if (date[0] > 30 and date[1] not in [1, 3, 5, 7, 8, 10, 12]):
            correct_date = False
        elif (date[1] == 2 and date[0] > 27):
            correct_date = False

        if (not correct_date):
            await ctx.send("Bruh! My expectation from you was low but holy shit!")

        bday_date, bday_month = date

        if (tz != "UTC"):
            list_of_timezones = list(pytz.all_timezones)
            
            for i in range(len(list_of_timezones)):
                if (tz.title() in list_of_timezones[i]):
                    tz = list_of_timezones[i]
                    break
            else:
                await ctx.send("Uh oh! Timezone not found 👀")
                await ctx.send("You can check list of timezones using `luci timezones [continent name]`")
                return

        try:
            self.cursor.execute("DELETE FROM bday WHERE id = {}".format(member.id))
            self.dbcon.commit()
        except:
            pass

        query = f"""INSERT INTO bday VALUES
                ({member.id}, {member.guild.id}, {bday_date}, {bday_month}, '{tz}')"""

        try:
            self.cursor.execute(query)
            self.dbcon.commit()
        except Exception as error:
            await ctx.send(f"```css\n{error}```")
            await ctx.send(str("Are you doing everything correctly?" + 
                "Might want to check usage `luci help bday set`" + 
                "Or if the problem persists ping `@Lucifer Chase`"))
        else:
            embed = discord.Embed(title = "Success! <a:nacho:839499460874862655>", color = 0x00FFFF)
            embed.add_field(name = "Member", value = member.nick)
            embed.add_field(name = "Date", value = "/".join(date))
            embed.add_field(name = "Timezone", value = tz)

            await ctx.send(embed = embed)

    @bday.command(name = "delete")
    async def bdaydelete(self, ctx):
        self.cursor.execute("DELETE FROM bday WHERE id = {}".format(ctx.author.id))
        self.dbcon.commit()

    @commands.command()
    @commands.is_owner()
    async def showbday(self, ctx):
        self.cursor.execute("SELECT * FROM bday")
        data = self.cursor.fetchall()

        await ctx.send("```css\n{}```".format(json.dumps(data[len(data)//2:], indent = 1)))
        await ctx.send("```css\n{}```".format(json.dumps(data[:len(data)//2], indent = 1)))

        not_redundant = []
        redundant = []
        for i in data:
            if (i[0] not in not_redundant):
                not_redundant.append(i[0])
            else:
                redundant.append(i[0])

        await ctx.send("```css\n{}```".format(json.dumps(redundant, indent = 2)))