from os import path
from glob import glob
from io import BytesIO

import discord
import aiohttp
from discord.ext import commands
from imagehash import phash
from PIL import Image


class RedditRepostBots(commands.Cog):
    """Reddit repost bots detection"""

    def __init__(self, bot):
        self.bot = bot
        self.hashes = dict()
        if path.exists("posted/"):
            for file in glob("posted/*"):
                self.hashes[file] = phash(Image.open(file))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id != 1294324881365930185 or not message.author.bot:
            return
        async with aiohttp.ClientSession() as sess:
            try:
                if len(message.embeds) > 0:
                    emb = message.embeds[0]
                    if emb.image and emb.image.proxy_url:
                        async with sess.get(emb.image.proxy_url) as resp:
                            buffer = BytesIO(await resp.read())
                            img = Image.open(buffer)
                            hash = phash(img)
                            for fn, hsh in self.hashes.items():
                                if hsh - hash < 5:
                                    await message.guild.get_channel(1345472948043120691).send(f"<@200282032771694593> repost detected. Hamming distance: **{hsh - hash}**. Original image: `{fn}`. Post URL: {emb.url}")
                                    await message.delete()
                                    break
            except Exception as e:
                print(e)


async def setup(bot):
    await bot.add_cog(RedditRepostBots(bot))

