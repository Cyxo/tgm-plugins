import json
from os import path

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel


CHANNEL_ID = 1293716015175176234


class Banshare(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel = self.bot.get_channel(CHANNEL_ID)

        self.banshared = {}
        if path.exists("banshared.json"):
            with open("banshared.json", "r") as f:
                self.banshared = json.load(f)

    @commands.Cog.listener("on_member_join")
    async def welcome_on_member_join(self, member: discord.Member):
        if self.channel is not None:
            if str(member.id) in self.banshared.keys():
                await self.channel.send(f"<@&1292946300865876142> The new member <@{member.id}> is in a banshare from partnered servers!\n"
                                        "Here was the reason: \"{self.banshared[str(member.id)]}\"")

    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command()
    async def banshare(self, ctx: commands.Context, id: int, *, reason: str):
        m = ctx.guild.get_member(id)
        if m is not None:
            await self.channel.send(":warning: The member is already in the server!")
        
        self.banshared[str(id)] = reason
        j = json.dumps(self.banshared)
        with open("banshared.json", "w") as f:
            f.write(j)
        await self.channel.send(f"<@{id}> added to the banshare list! Reason: \"{reason}\"")

    @checks.has_permissions(PermissionLevel.MODERATOR)
    @commands.command()
    async def banshare_info(self, ctx: commands.Context, member: discord.Member):
        id = member.id
        if str(id) in self.banshared.keys():
            await ctx.reply(f'{member.mention} is in the banshare list: "{self.banshared[str(id)]}"')
        else:
            await ctx.reply(f'{member.mention} is not in the banshare list.')


async def setup(bot):
    await bot.add_cog(Banshare(bot))
