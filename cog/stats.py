import discord, json, PIL, easy_pil, os
from other.request_data import *
from discord import Option
from discord.ext import commands
from bot import bot
from PIL import Image
from easy_pil import Editor, load_image_async, Font

color = int(os.getenv("color"), 16)

with open("data/emojis.json") as emojis_json_file:
    emojis_json = json.load(emojis_json_file)
    emojis_json_file.close()

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def stats(self, ctx: discord.ApplicationContext, username: Option(str, "Enter your IGN")):
        await ctx.defer()
        data = get_all(username, False)
        embed = discord.Embed(
            title=f"Account Information for {data['username']}",
            description="",
            color=color,
            url=f"https://sky.noms.tech/stats/{username}"
        )
        background = Editor(f"images/blank_1000.png")
        if "ADMIN" in data["rank"]:
            rank = Editor(f"images/admin_rank.png").resize((975, 225))
        elif "YOUTUBE" in data["rank"]:
            rank = Editor(f"images/youtube_rank.png").resize((975, 225))
        elif "SUPERSTAR" in data["rank"]:
            rank = Editor(f"images/mvp++_rank.png").resize((975, 225))
        elif "MVP+" in data["rank"]:
            rank = Editor(f"images/mvp+_rank.png").resize((975, 225))
        elif "MVP" in data["rank"]:
            rank = Editor(f"images/mvp_rank.png").resize((975, 225))
        elif "VIP+" in data["rank"]:
            rank = Editor(f"images/vip+_rank.png").resize((975, 225))
        elif "VIP" in data["rank"]:
            rank = Editor(f"images/vip_rank.png").resize((975, 225))
        else:
            rank = Editor(f"images/non_rank.png").resize((975, 225))

        background.paste(rank, (0, 387))

        thumbnail = discord.File(fp=background.image_bytes, filename="rank.png")
        embed.add_field(name=f"{emojis_json['skillAverage']} Skill Average", value=f"{data['skillAverage']}")
        embed.add_field(name=f"{emojis_json['catacombs']} Catacombs", value=f"{data['dungeonLevel']}")
        embed.add_field(name=f"{emojis_json['weight']} Weight", value=f"{data['weight']}")
        embed.add_field(name=f"{emojis_json['skyblockLevel']} SkyBlock Level:", value=f"{data['skyblockLevel']}", inline=True)
        embed.add_field(name=f"{emojis_json['slayer']} Slayer",
                        value=f"{data['zombie']} / {data['spider']} / {data['wolf']} / {data['enderman']} / {data['blaze']} / {data['vampire']}")
        embed.add_field(name=f"{emojis_json['networthBank']} Networth:",
                        value=f"{data['networth']} (Soulbound: {data['soulboundNetworth']}) - Coins: {data['coins']}",
                        inline=False)
        embed.add_field(name=f"{emojis_json['hotm']} HOTM",
                        value=f"{emojis_json['hotmLevel']} HOTM Level: \n{emojis_json['mithrilPowder']} Mithril Powder: {data['mithrilPowder']}\n{emojis_json['gemstonePowder']} Gemstone Powder: {data['gemstonePowder']}",
                        inline=True)
        embed.add_field(name=f"{emojis_json['crimsonIsle']} Crimson Isle",
                        value=f"{emojis_json['faction']} Faction: {data['faction']}\n{emojis_json['mageRep']} Mage rep: {data['mages_reputation']}\n{emojis_json['barbRep']} Barbarian rep: {data['barbarians_reputation']}", inline=True)
        embed.set_thumbnail(url=f"attachment://{thumbnail.filename}")
        await ctx.edit(embed=embed, file=thumbnail)


def setup(bot):
    bot.add_cog(Stats(bot))
