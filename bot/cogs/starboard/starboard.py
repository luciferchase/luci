import discord
from discord.ext import commands


class Starboard(commands.Cog):
    """Remember your wildest moments"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
        if (payload.guild_id != 847116716646727740):
            return

        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

        for reaction in message.reactions:
            if (reaction.emoji.name == ":star:" and reaction.count == 5):
                await message.add_reaction("✅")

                channel = await self.bot.fetch_channel(847325243780366346)

                embed = discord.Embed(title = message.author.nick, colour = 0x00FFFFF)
                embed.add_field(name = "Source", value = f"[Jump to message]({message.url})", inline = False)
                embed.add_field(name = "Channel", value = message.channel.mention, inline = False)
                embed.set_author(icon_url = message.author.avatar_url)
                embed.set_footer(text = message.created_at.strftime("%d-%m-%Y | %H:%M"))
                
                if (message.content):
                    embed.description(message.content)
                if (message.attachments):
                    embed.set_image(url = message.attachments[0].url)

                await channel.send(embed = embed)