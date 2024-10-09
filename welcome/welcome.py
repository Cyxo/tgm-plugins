import discord
from discord.ext import commands


CHANNEL_ID = 1292913818573209690


class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def welcome_on_member_join(self, member: discord.Member):
        guild = member.guild
        channel = self.bot.get_channel(CHANNEL_ID)
        if channel is not None:
            embed = discord.Embed(
                title=f"Welcome to Trigger Mains, {member.name}!",
                description=f"Please read <#1292914076967501987> and accept the rules to access the rest of the server!\n\nYou can also visit <#1292914884396453899> to familiarize yourself with the server, and <#1292917244678115339> to claim some additional roles!\n\n We wish you a pleasant stay; if you need help, DM <@1293642317298663526> to start a Modmail ticket!",
                colour=discord.Colour.from_rgb(84, 140, 140)
            )

            embed.set_thumbnail(url=member.display_avatar)
            embed.set_image(
                url='https://media.discordapp.net/attachments/1293249412856025149/1293690609575530556/trigger_sniper.png')
            embed.set_footer(text=f'Thanks to you, we now have {guild.member_count} members!') # ,
                             # icon_url='https://cdn.discordapp.com/attachments/1106792127268139119/1153168727701995620/ruanmei_flower.png')

            await channel.send(content=member.mention, embed=embed)


async def setup(bot):
    await bot.add_cog(Welcome(bot))
