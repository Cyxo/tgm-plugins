import asyncio
import json
import uuid
from os import path

import discord
import aiohttp
from bs4 import BeautifulSoup
from discord.ext import commands


CONF_FILE = path.join(path.dirname(__file__), "config.json")
SETTINGS = {
    "channel_id": int,
    "subreddit": str,
    "cookies": json.loads,
    "ignore_nsfw": lambda v: v == "True"
}
COG_NAME = "RedditFeed"


@discord.app_commands.default_permissions(administrator=True)
class RedditFeed(commands.GroupCog, name=COG_NAME, group_name="reddit"):
    """Reddit repost bots detection"""

    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.cog_id = uuid.uuid4()

        self.last_entry = None

        self.channel_id = 1294324881365930185
        self.subreddit = "TriggerMains"
        self.cookies = None
        self.ignore_nsfw = True

        self.load_conf()
        self.save_conf()

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:148.0) Gecko/20100101 Firefox/148.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'fr,fr-FR;q=0.9,en-US;q=0.8,en;q=0.7',
            'Prefer': 'safe',
            # 'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Referer': 'https://old.reddit.com/r/TriggerMains/',
            'Connection': 'keep-alive',
            # 'Cookie': 'loid=0000000000000nzbn0.2.1433784918724.Z0FBQUFBQm85X001LW82M3NEWEJIcGRONFJSenlOQ01ZZXFvMHZneTBDZGdmdDFXZkw0S2ZoWTlKallvRV95empfZnNpTHB4TzdJSmN0NXF3bVg3WWlncDhzd25TOVhuaDlJY2NzWUtpMU5reTNaWnhzdTcxMl9WcjV0RGFJVlhxeGo3SElLMURBOC0; csv=2; edgebucket=Usaz1r6MzRoRba4Fov; reddit_session=eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpsVFdYNlFVUEloWktaRG1rR0pVd1gvdWNFK01BSjBYRE12RU1kNzVxTXQ4IiwidHlwIjoiSldUIn0.eyJzdWIiOiJ0Ml9uemJuMCIsImV4cCI6MTc4ODM0MDk1NS4wNzIyOTIsImlhdCI6MTc3MjcwMjU1NS4wNzIyOTIsImp0aSI6IjVlM2FkOTBhdkppQzR6U2lwVXhCZTdEMlQyZ0xlZyIsImF0IjoxLCJjaWQiOiJjb29raWUiLCJsY2EiOjE0MzM3ODQ5MTg3MjQsInNjcCI6ImVKeUtqZ1VFQUFEX193RVZBTGsiLCJmbG8iOjIsImFtciI6WyJwd2QiXX0.UVN8dZBvig-EjBckjmCHUSxpR5OZ7Giak9s5u2RoOHXBrEbk_kIYQg_ly42Zsb-8zXG4m1rvw27kdsX-YczsRSqknUE5Is-fzzEyWpt6EiOnuTjvSwdtlIaPQyIRPMgQxBIfi1U9zEMtgradiihnUP2qO0f_lkeFcNgo_ZMSK8i54hXbj0uHl8RvJPKI5O2gv1q4fP4XcEYxmN8lJivSW1nxxtxhD2NqnymPO_X6CAniDF55jXX-Rgga0kRtFV5CwaisufDGJN1Bv2cIhFzpYYAfbhyLe6Puo6TM7IMR48BSlyhHVGGK0JJrqD21Rc_574uehD6jXx9ZkW-b7kCNfw; theme=2; t2_nzbn0_recentclicks3=t3_1rnw208%2Ct3_1f0upey%2Ct3_1rjx5v6%2Ct3_1rd8f8h%2Ct3_1rg1gpr%2Ct3_1re7pan%2Ct3_1ri1jx9%2Ct3_1rilo74%2Ct3_1rjbhtp%2Ct3_67osc8; pc=ek; eu_cookie=%7B%22opted%22%3Atrue%2C%22nonessential%22%3Afalse%7D; csrf_token=f725d1c6379954be016941840f89aba2; session_tracker=hpfgqlrifjbcemjlhp.0.1773068764239.Z0FBQUFBQnBydUhjRnJXM0lGWHE0RnljMEl1VEM2NUxOVEc4VjBVd2xoeTNhdlVfTWlYa1RMTjkwUW5RekxoUFFHblV0MGZoWWhWUVloOW9pbTFaOEd1eGlvX3h1UXVHSlEyWFRHWnlwSnNJNWdnZVFMN3ByLVZva3V1TGhIclhLV3UxeUZWMFRnWDc; token_v2=eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpzS3dsMnlsV0VtMjVmcXhwTU40cWY4MXE2OWFFdWFyMnpLMUdhVGxjdWNZIiwidHlwIjoiSldUIn0.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNzczMTU1MTQ0Ljg2NDk4OSwiaWF0IjoxNzczMDY4NzQ0Ljg2NDk4OSwianRpIjoic1Z0cDgwRXJHUVJuRmc1YzEtRlBRWS1NMm1wWWxRIiwiY2lkIjoiMFItV0FNaHVvby1NeVEiLCJsaWQiOiJ0Ml9uemJuMCIsImFpZCI6InQyX256Ym4wIiwiYXQiOjEsImxjYSI6MTQzMzc4NDkxODcyNCwic2NwIjoiZUp4a2tkR090REFJaGQtRmE1X2dmNVVfbTAxdGNZYXNMUWFvazNuN0RWb2NrNzA3Y0Q0cEhQOURLb3FGRENaWGdxbkFCRmdUclREQlJ1VDluTG0zZzJpTmU4dFlzWm5DQkZtd0ZEcmttTEdzaVFRbWVKSWF5eHNtb0lMTnlGeXV0R05OTFQwUUpxaGNNcmVGSHBjMm9ia2JpNTZkR0ZXNXJEeW9zVmZsMHRqR0ZMWW54amNicXcycHVDNm5Na25MUXZrc1h2VGpOOVczOXZtel9TYTBKOE9LcXVtQjNobEpDRzRzZnBpbTNkOVRrNTZ0Q3hhMTkzcVEydWQ2M0s1OTFpdzBPN2VmNl9sckl4bVhZMmgtSnZ0MzF5LWhBNDg4THpQcUFFYXM0VWNaZG1RZF9sVUhVTG1nSkdNSjR0TUk1TXJsMjM4SnRtdlR2OGJ0RXo5OE0tS21OX3pXRE5SekNlTFFwX0gxR3dBQV9fOFExZVRSIiwicmNpZCI6IjNwVGVObUE2Nmg5ZExRS085NWdhSVJHWE5zMllRazV2UTM0LTZWMmwwSUEiLCJmbG8iOjJ9.VGlO4jXbfRX8-R0KO9VY8ETKZW_JDT-fYcZ1IXiT6i2cZeaD8mqAJQx77UIH7W_F01h9PT91e1b-yJhmuVw4dzvy-7yO-zo0IhffeGgwg-9Fb1YjPUfye0AbY3EFlH5T8Da-rfasnEgRWNEoxS0itFpRJI0rt-HZAD0IFj_Vd4yLZ41AsM48b2hq5lXgdgG_H_bINvIGDAlHZat-vkqfKz5mLiRuIDwzi4FnLrIo75_arTyQvC6qY7JmAQaV9wW6MoLtv2yKPIdhQ7xa4TI3IFkQ9XBCPe9KpdMlx7nLGN0-98mnQzHhmx9AMzbksPhPXmVOLMgp-lpB_5O0x_BbkQ; seeker_session=false',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Priority': 'u=0, i',
            # Requests doesn't support trailers
            # 'TE': 'trailers',
        }

    def load_conf(self):
        if path.exists(CONF_FILE):
            with open(CONF_FILE, "r") as f:
                j = json.load(f)
                self.last_entry = j["last_entry"]
                for setting in SETTINGS.keys():
                    setattr(self, setting, j[setting])

    def save_conf(self):
        j = json.dumps({
            "last_entry": self.last_entry,
        } | {
            setting: getattr(self, setting)
            for setting in SETTINGS.keys()
        })
        with open(CONF_FILE, "w+") as f:
            f.write(j)

    async def get_new_entries(self):
        print("Reddit feed scheduling started")
        while True:
            cog: RedditFeed = self.bot.get_cog(COG_NAME)
            if cog is None or cog.cog_id != self.cog_id:
                print("Reddit feed cog out of date, exitting")
                break

            if self.cookies is None:
                await asyncio.sleep(1)
                continue

            channel = self.bot.get_channel(self.channel_id)

            async with aiohttp.ClientSession("https://old.reddit.com/", cookies=self.cookies, headers=self.headers) as session:
                async with session.get(f"/r/{self.subreddit}/new/") as r:
                    html = await r.text()

                soup = BeautifulSoup(html, "html.parser")

                posts = soup.find_all("div", {"class": "thing"})
                for post in posts:
                    if post["id"] == self.last_entry:
                        break

                    if post.find("div", {"class": "nsfw-stamp"}) and self.ignore_nsfw:
                        continue

                    rel_link = post["data-permalink"]
                    link = f"https://www.rxddit.com{rel_link}"

                    await channel.send(link)

                    if self.last_entry is None:
                        break

                self.last_entry = posts[0]["id"]
                self.save_conf()

            await asyncio.sleep(60)

    @discord.app_commands.command()
    @discord.app_commands.choices(name=[
        discord.app_commands.Choice(name=k, value=k)
        for k in SETTINGS.keys()
    ])
    async def setting(self, interaction: discord.Interaction, name: str, value: str):
        func = SETTINGS[name]
        setattr(self, name, func(value))
        self.save_conf()
        await interaction.response.send_message(f"Setting `{name}` set to `{getattr(self, name)}`")


async def setup(bot: commands.Bot):
    cog = RedditFeed(bot)
    await bot.add_cog(cog)
    await bot.tree.sync()
    asyncio.get_event_loop().create_task(cog.get_new_entries())
    print("Reddit Feed installed")
