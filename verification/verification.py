import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

CHANNEL_ID = 1292914076967501987
MESSAGE_ID = 1293705204872777800
PING_THREAD_ID = 1293684881599234088
ROLE_ID = 1292910842462867478


class Verification(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_raw_reaction_add")
    async def verification_on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        message_id = payload.message_id
        msg = await self.bot.get_channel(CHANNEL_ID).fetch_message(MESSAGE_ID)
        if message_id != msg.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = payload.member
        if payload.emoji.name == '🔫':
            await msg.remove_reaction('🔫', member)
        elif payload.emoji.name == '✅':
            ping_thread = self.bot.get_channel(CHANNEL_ID).get_thread(PING_THREAD_ID)
            await ping_thread.send(f"{payload.member.mention} lying is bad, you should read the rules for real !! (I promise they're not *that* long)")
            await ping_thread.remove_user(payload.member)
            return
        else:
            # Remove other types of reactions
            return await msg.remove_reaction(payload.emoji, member)

        # Get Butterflies role
        role = discord.utils.get(guild.roles, id=ROLE_ID)
        # If member exists, is not a bot and doesn't have the Muted Role
        if member is not None and not member.bot:
            await member.add_roles(role)

    # In case all reactions get cleared
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    @commands.command()
    async def fixreaction(self, ctx: commands.Context):
        """Fixes the reactions in verification channel"""
        # Get Message object from the Verification Channel
        channel = self.bot.get_channel(CHANNEL_ID)
        msg = await channel.fetch_message(MESSAGE_ID)
        emojis = set([reac.emoji for reac in msg.reactions])
        for emoji in emojis:
            if emoji != '✅':
                await msg.clear_reaction(emoji)
        await msg.add_reaction('✅')

        await ctx.send(embed=discord.Embed(description='Reaction added!', colour=discord.Colour.from_rgb(0, 255, 0)))


async def setup(bot):
    await bot.add_cog(Verification(bot))
