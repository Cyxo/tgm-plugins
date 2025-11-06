from os import path
from glob import glob

import discord
import aiohttp
from discord.ext import commands
from imagehash import phash
from PIL import Image


class RedditRepostBots(commands.Cog):
    """Reddit repost bots detection"""

    def __init__(self, bot):
        self.bot = bot
        self.hashes = []
        if path.exists("posted/"):
            for file in glob("posted/*"):
                self.hashes.append(phash(Image.open(file)))

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
        async with aiohttp.ClientSession() as sess:
            i = 0
            async for msg in message.channel.history():
                try:
                    if len(msg.embeds) > 0:
                        emb = msg.embeds[0]
                        if emb.image and emb.image.proxy_url:
                            async with sess.get(emb.image.proxy_url) as resp:
                                fname = emb.image.proxy_url.split("/")[-1].split("?")[0]
                                with open(f"posted/{fname}", "wb+") as f:
                                    f.write(await resp.read())
                                    i += 1
                                    print(i)
                except Exception as e:
                    print(e)


async def setup(bot):
    await bot.add_cog(RedditRepostBots(bot))

