import discord
from discord.ext import commands


class Starboard(commands.Cog):
    """Remember your wildest moments"""

    def __init__(self, bot):
        self.bot = bot

    async def format_embed(self, message):
        await message.add_reaction("✅")

        channel = await self.bot.fetch_channel(848815102664114176)

        embed = discord.Embed(title = message.author.nick)
        embed.add_field(name = "Source", value = f"[Jump to message]({message.jump_url})", inline = True)
        embed.add_field(name = "Channel", value = message.channel.mention, inline = True)
        embed.set_author(
            name = f"{message.author.name}#{message.author.discriminator}", 
            icon_url = message.author.avatar_url
        )
        embed.set_footer(text = message.created_at.strftime("%d-%m-%Y | %H:%M"))
        
        if (message.content):
            embed.description = message.content
        if (message.attachments):
            embed.set_image(url = message.attachments[0].url)

        await channel.send(embed = embed)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if (payload.guild_id != 587139618999369739 or payload.channel_id == 848244705254441040 \
            or payload.user_id == 836213550384545852):
            return

        message = await self.bot.get_channel(payload.channel_id).fetch_message(payload.message_id)

        if (payload.emoji.name == "🏆"):
            if (payload.member.guild_permissions.manage_messages):
                for reaction in message.reactions:
                    if (reaction.emoji == "🏆" and reaction.count == 1):
                        await self.format_embed(message)
                return
        elif (payload.emoji.name == "⭐"):
            for reaction in message.reactions:
                if (reaction.emoji == "⭐" and reaction.count == 6):
                    await self.format_embed(message)

