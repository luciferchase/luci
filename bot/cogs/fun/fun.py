import discord
from discord.ext import commands

import aiohttp
from datetime import datetime
import re

class Fun(commands.Cog):
    """Various fun commands"""
    def __init__(self, bot):
        self.bot = bot
        # Initialize a session
        self.session = aiohttp.ClientSession()

    @commands.command(aliases = ["nda", "nato"])
    async def alphanato(self, ctx, *args):
        """Get military phonetics of every letter in english alphabet.
        Usage: You can get all the phonetics by simply calling `luci nda` or `luci alphanato`
        
        You can also get phonetics for a particular letter or multiple letter (separated by space) by doing:
        `luci nda l` or `luci nda l m n o`"""
        
        phonetics = ["Alpha", "Bravo", "Charlie", "Delta", "Echo", "Foxtrot", "Golf",\
        "Hotel", "India", "Juliett", "Kilo", "Lima", "Mike", "November", "Oscar", "Papa", \
        "Quebec", "Romeo", "Sierra", "Tango", "Uniform", "Victor", \
        "Whiskey", "X-Ray", "Yankee", "Zulu"]

        message_string = ""

        if (args == ()):
            for index in range(26):
                message_string += f"{chr(97 + index)}: {phonetics[index]}\n"

        else:
            for letter in args:
                mssg_string += f"{letter}: {''.join([i for i in phonetics if i[0].lower() == letter])}\n"

        await ctx.send(f"```ml\n{mssg_string}```")

    @commands.command(aliases = ["av"])
    async def avatar(self, ctx, *, user: discord.Member = None):
        """Returns user avatar URL.

        User argument can be user mention, nickname, username, user ID.
        Default to yourself when no argument is supplied.
        """
        author = ctx.author

        if not user:
            user = author

        if user.is_avatar_animated():
            url = user.avatar_url_as(format = "gif")
        if not user.is_avatar_animated():
            url = user.avatar_url_as(static_format = "png")

        await ctx.send("{}'s Avatar URL : {}".format(user.name, url))
    
    @commands.command()
    async def catfact(self, ctx):
        """Get a random fact about cats."""
        async with self.session.get("https://catfact.ninja/fact") as response:
            data = await response.json()
            fact = data["fact"]

            embed = discord.Embed(title = "Catfact ❤", description = fact, color = 0x00ffff)
            await ctx.send(embed = embed)

    @commands.command()
    async def dogfact(self, ctx):
        """Get a random fact about dogs. [Bit slow to run for the first time though (API limitation)]"""
        async with self.session.get(
            "https://dog-facts-api.herokuapp.com/api/v1/resources/dogs?number=1") as response:
            data = await response.json()
            fact = data[0]["fact"]

            embed = discord.Embed(title = "Dogfact ❤", description = fact, color = 0x00ffff)
            await ctx.send(embed = embed)

    @commands.command(aliases = ["roast"])
    async def insult(self, ctx, member: discord.Member = None):
        """Insult someone. They are really evil though, take care."""

        if (member is None):
            member = ctx.author

        async with self.session.get("https://evilinsult.com/generate_insult.php") as response:
            text = await response.text()

            embed = discord.Embed(
                title = f"{ctx.author.name} insulted {member.name}",
                description = text,
                color = 0xf34949
            )
            await ctx.send(embed = embed)

    async def _check_if_down(self, url_to_check):
        re_compiled = re.compile(r"https?://(www\.)?")
        url = re_compiled.sub("", url_to_check).strip().strip("/")

        url = f"https://isitdown.site/api/v3/{url}"
        
        # log.debug(url)
        async with self.session.get(url) as response:
            assert response.status == 200
            resp = await response.json()
        return resp, url

    @commands.command(alias=["iid"])
    async def isitdown(self, ctx: commands.Context, url_to_check):
        """
        Check if the provided url is down
        Alias: iid
        """
        try:
            resp, url = await self._check_if_down(url_to_check)
        except AssertionError:
            await ctx.send("Invalid URL provided. Make sure not to include `https://`")
            return

        # log.debug(resp)
        if resp["isitdown"]:
            await ctx.send(f"{url} is DOWN!")
        else:
            await ctx.send(f"{url} is UP!")

    @commands.command(aliases = ["saabit"])
    async def joke(self, ctx):
        async with self.session.get("https://icanhazdadjoke.com/", 
            headers = {"Accept": "application/json"}) as response:
            data = await response.json()

            if (data["status"] > 200):
                await ctx.send(f"Uh Oh! I faced some issue <a:awkward1:839499334555140157>")
                return

            await ctx.send(f"> {data['joke']}")
            await ctx.send("<:eZZ:791575889526652949>")

    @commands.guild_only()
    @commands.command(aliases = ["n"])
    async def nitro(self, ctx, emoji_name):
        """Send an animated emoji even if you don't have nitro. \
        Send just its name and the bot will send the emote.
        Usage: `luci n nacho`"""

        # # Delete original message
        # await ctx.message.delete()

        # First get all the emojies the bot has access and then Send emoji
        emoji_found = False
        for emoji in self.bot.emojis:
            if (emoji.name in emoji_name):
                await ctx.send(emoji.url)
                emoji_found = True

        if (not emoji_found):
            await ctx.send("Emoji not found <a:awkward1:839499334555140157>")
    
    @commands.guild_only()
    @commands.command()
    async def poll(self, ctx, *message):
        """Do a poll
        Syntax: luci poll <question> |option 1|option 2|option 3|...
        For eg: luci poll Is luci geh? |Yes|No|You are geh|
        You can omit options to make it automatically a two option poll
        """

        # Delete original message
        await ctx.message.delete()

        message = " ".join(message)
        time = datetime.now().strftime("%m/%d/%Y %H:%M:%S")

        # CHeck if there is an actual question given or not
        if (len(message) == 0):
            await ctx.send("Bruh! Send a question atlease 🤦‍♂️")
            # await ctx.invoke(self.bot.get_command("help"), "dm")
            return

        # Get index of question and options separator "|"
        index = message.find("|")

        # Check if there are any options or not
        if (index != -1):
            # Get question and options from the message
            question = message[:message.find("|")]
            options = [option for option in message[message.find("|") + 1:].split("|") if option != ""]

            # Check if there are more than 26 options
            if (len(options) > 20):
                await ctx.send("Bruh! Please give maximum 20 options 🤦‍♂️.",
                    " You can only react 20 times to a message.")
                return

            reactions = ["🇦", "🇧", "🇨", "🇩", "🇪", "🇫", "🇬", "🇭", "🇮", "J", "🇰", "🇱", "🇲", "🇳", "🇴", "🇵", \
            "🇶", "🇷", "🇸", "🇹", "🇺", "🇻", "🇼", "🇽", "🇾", "🇿"]

            options_string = ""
            for index in range(len(options)):
                options_string += f"{reactions[index]} {options[index]}\n"

            embed = discord.Embed(
                title = question,
                description = options_string,
                color = 0x00FFFF
            )
            embed.set_footer(text = time)
            embed.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)

            poll_embed = await ctx.send(embed = embed)

            for index in range(len(options)):
                await poll_embed.add_reaction(reactions[index])
            
        # Else by default make a dual option poll
        else:
            question = "".join(message)

            embed = discord.Embed(
                title = question,
                color = 0x00FFFF
            )
            embed.set_footer(text = time)
            embed.set_author(name = ctx.author.name, icon_url = ctx.author.avatar_url)

            poll_embed = await ctx.send(embed = embed)
            await poll_embed.add_reaction("👍")
            await poll_embed.add_reaction("👎")

    @commands.command(aliases = ["emojify", "cry"])
    async def shout(self, ctx, *message):
        """Convert a message into emojies"""

        # # Delete original message
        # await ctx.message.delete()
        
        final_message = []

        for word in message:
            message_string = ""

            for letter in word:
                message_string += f":regional_indicator_{letter.lower()}: "
            final_message.append(message_string)

        await ctx.send(" ".join(final_message))

    @commands.command()
    @commands.cooldown(rate=1, per=2.0, type = commands.BucketType.user)
    async def urban(self, ctx, *, search: commands.clean_content):
        """ Find the 'best' definition to your words """
        async with ctx.channel.typing():
            try:
                async with self.session.get(f"https://api.urbandictionary.com/v0/define?term={search}") \
                as response:
                    data = await response.json()
            except Exception:
                return await ctx.send("Urban API returned invalid data... might be down atm.")

            if not len(data["list"]):
                return await ctx.send("Couldn't find your search in the dictionary...")

            result = sorted(data["list"], reverse = True, key=lambda i: int(i["thumbs_up"]))[0]

            definition = result["definition"]

            if len(definition) >= 1000:
                definition = definition[:1000]
                definition = definition.rsplit(" ", 1)[0]
                definition += "..."

            await ctx.send(f"📚 Definitions for **{result['word']}**```fix\n{definition}```")