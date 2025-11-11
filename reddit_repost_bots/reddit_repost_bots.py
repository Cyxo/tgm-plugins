import re
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
        self.bot: discord.Client = bot
        self.hashes = dict()
        if path.exists("posted/"):
            for file in glob("posted/*"):
                self.hashes[file] = phash(Image.open(file))

    async def on_ready(self):
        print("Loading posted images")
        async with aiohttp.ClientSession() as sess:
            i = 0
            async for msg in self.bot.get_guild(1292899450754302024).get_channel(1294324881365930185).history():
                try:
                    if len(msg.embeds) > 0:
                        emb: discord.Embed = msg.embeds[0]
                        url = None
                        detecc = re.findall(r"https?://i.imgur.com/\w+.\w+", emb.description)
                        if emb.image and emb.image.url:
                            url = emb.image.url
                        elif emb.image and emb.image.proxy_url:
                            url = emb.image.proxy_url
                        elif len(detecc) > 0:
                            url = detecc[0]
                        if url is not None:
                            fname = url.split("/")[-1].split("?")[0]
                            if not path.exists(f"posted/{fname}"):
                                async with sess.get(emb.image.proxy_url) as resp:
                                    if resp.status == 200:
                                        with open(f"posted/{fname}", "wb+") as f:
                                            f.write(await resp.read())
                                            i += 1
                                            print(f"{i}. {fname}")
                except Exception as e:
                    print(e)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.channel.id != 1294324881365930185 or not message.author.bot:
            return
        async with aiohttp.ClientSession() as sess:
            try:
                if len(message.embeds) > 0:
                    emb = message.embeds[0]
                    url = None
                    detecc = re.findall(r"https?://i.imgur.com/\w+.\w+", emb.description)
                    if emb.image and emb.image.url:
                        url = emb.image.url
                    elif emb.image and emb.image.proxy_url:
                        url = emb.image.proxy_url
                    elif len(detecc) > 0:
                        url = detecc[0]
                    if url is not None:
                        async with sess.get(url) as resp:
                            buffer = BytesIO(await resp.read())
                            img = Image.open(buffer)
                        hash = phash(img)
                        found = False
                        for fn, hsh in self.hashes.items():
                            if hsh - hash < 5:
                                await message.guild.get_channel(1345472948043120691).send(f"<@200282032771694593> repost detected. Hamming distance: **{hsh - hash}**. Original image: `{fn}`. Post URL: {emb.url}")
                                await message.delete()
                                found = True
                                break
                        if not found:
                            fn = url.split("/")[-1].split("?")[0]
                            img.save(f"posted/{fn}")

            except Exception as e:
                print(e)


async def setup(bot):
    cog = RedditRepostBots(bot)
    await bot.add_cog(cog)
    await cog.on_ready()

