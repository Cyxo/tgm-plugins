import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

CHANNEL_ID = 1292914076967501987
MESSAGE_ID = 1293705204872777800
PING_THREAD_ID = 1293684881599234088
ROLE_ID = 1292910842462867478


MESSAGES = [
    "lying is bad, you should read the rules for real !! (I promise they're not *that* long)",
    "the verification is not broken! Reading the rules will tell you how to verify!",
    "you're one stubborn child... Stop clicking that ✅ and read the rules!",
    "okay, I'll give you a tip. The answer is in the 6th rule category 😉",
    "is it too hard for you to read? 😭",
    "I'm starting to think that you're teasing me...",
    "imma call Soldier 11 to punish you if you don't read the rules!",
    "stop, this ain't fun anymore. Read the rules. 😐"
]


class Verification(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.time_sent = {}

    @commands.Cog.listener("on_raw_reaction_add")
    async def verification_on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        message_id = payload.message_id
        ping_thread = self.bot.get_guild(payload.guild_id).get_channel_or_thread(PING_THREAD_ID)
        msg = await self.bot.get_channel(CHANNEL_ID).fetch_message(MESSAGE_ID)
        if message_id != msg.id:
            return

        guild = self.bot.get_guild(payload.guild_id)
        member = payload.member
        if payload.emoji.name == '🔫' or ping_thread is None:
            await msg.remove_reaction('🔫', member)
        elif payload.emoji.name == '✅':
            if payload.user_id not in self.time_sent:
                self.time_sent[payload.user_id] = 0
            idx = min(self.time_sent[payload.user_id], len(MESSAGES) - 1)
            await ping_thread.send(payload.member.mention + " " + MESSAGES[idx])
            self.time_sent[payload.user_id] += 1
            return
        else:
            # Remove other types of reactions
            return await msg.remove_reaction(payload.emoji, member)

        # Get Butterflies role
        role = discord.utils.get(guild.roles, id=ROLE_ID)
        # If member exists, is not a bot and doesn't have the Muted Role
        if member is not None and not member.bot:
            await member.add_roles(role)
            try:
                await ping_thread.remove_user(payload.member)
            except:
                pass

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
