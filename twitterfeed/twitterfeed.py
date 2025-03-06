import re
import uuid

import aiocron
import aiohttp
import discord
import feedparser
from discord.ext import commands


CHANNEL_ID = 435078369852260353
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
NITTER_URL = "https://nitter.poast.org/{}/rss"
TWITTER_URL = "https://fxtwitter.com/Trigger_zzz/status/{}#m"
FEEDS = [
    "Trigger_zzz",
    "_dailytrigger"
]

COG_NAME="TwitterFeed"


def get_tweet_id(link: str):
    return re.match(r"https?://.*/(\d+).*", link).group(1)


class TwitterFeed(commands.Cog, name=COG_NAME):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cog_id = uuid.uuid4()
        self.session = aiohttp.ClientSession(headers={
            "User-Agent": USER_AGENT
        })
        self.posted: dict[str, list[str]] = {}
        self.index = 0

        self.cron = aiocron.crontab('*/15 * * * *', func=self.check_feeds)

    def init_posted(self, username, entries):
        self.posted[username] = []
        for entry in entries:
            if entry['title'].startswith('R to ') or entry['title'].startswith('RT by '):
                continue
            self.posted[username].append(get_tweet_id(entry['link']))

        print("Initial tweets for", username, ":", self.posted[username])

    async def check_feeds(self):
        cog: TwitterFeed = self.bot.get_cog(COG_NAME)
        if cog is None or cog.cog_id != self.cog_id:
            # We are in an old cog after update and don't have to send QOTD anymore
            await self.session.close()
            self.cron.stop()
            return

        username = FEEDS[self.index]

        async with self.session.get(NITTER_URL.format(username)) as r:
            if r.status == 200:
                txt = await r.text()
                rss = feedparser.parse(txt)
                if username not in self.posted.keys():
                    self.init_posted(username, rss['entries'])
                else:
                    i = 0
                    for entry in rss['entries']:
                        tweet_id = get_tweet_id(entry['link'])
                        if (entry['title'].startswith('R to ') or entry['title'].startswith('RT by ')) and not tweet_id in self.posted():
                            channel = self.bot.get_channel(CHANNEL_ID)
                            await channel.send(TWITTER_URL.format(tweet_id))
                        if i == 0:
                            channel = self.bot.get_channel(CHANNEL_ID)
                            await channel.send(TWITTER_URL.format(tweet_id))
                        i += 1
            else:
                print("Twitter feed error:", r.status, await r.text())

        self.index = (self.index + 1) % len(FEEDS)


async def setup(bot):
    await bot.add_cog(TwitterFeed(bot))
