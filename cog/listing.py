import discord, json, PIL, easy_pil, aiosqlite, os
from other.request_data import *
from discord import Option
from discord.ext import commands
from bot import bot
from PIL import Image
from easy_pil import Editor, load_image_async, Font
from other.listing_view import listingButtons

load_dotenv(".env")
color = int(os.getenv("color"), 16)
account_listing_category = int(os.getenv("account_listing_category"))
transcript_channel_id = int(os.getenv("transcript_channel_id"))
acc_ping_role = int(os.getenv("acc_ping_role"))



with open("data/emojis.json") as emojis_json_file:
    emojis_json = json.load(emojis_json_file)
    emojis_json_file.close()

async def get_last_entry():
    async with aiosqlite.connect(f"data/database.db") as db:
        async with db.execute("SELECT id FROM listing ORDER BY id DESC LIMIT 1") as cursor:
            second_last_entry = await cursor.fetchone()
            if second_last_entry is None:
                second_last_entry = (0,)
            last_entry = second_last_entry[0] + 1
            return last_entry


async def insert_in_db(price, uuid, channel_id, message_id, author_name, author_id, data, skyhelper, hypixel):
    async with aiosqlite.connect(f"data/database.db") as db:
        await db.execute(
            "INSERT INTO listing (uuid, price, channel_id, message_id, author_name, author_id, data, skyhelper_data, hypixel_data) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (uuid, price, channel_id, message_id, author_id, author_name, json.dumps(data), json.dumps(skyhelper), json.dumps(hypixel),))
        await db.commit()


class listing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.slash_command()
    async def list(self,
                   ctx: discord.ApplicationContext,
                   username: Option(str, "Enter your IGN"),
                   price: Option(str, f"Enter the price you wanna list the acc for!"),
                   payment_methods: Option(str, "Enter the payment methods u accept"),
                   show_ign: Option(bool)):
        await ctx.defer(ephemeral=True)
        data = get_all(username, False)
        if "$" not in price:
            price = f"${price}"
        channel_name = f"💲{price}｜account-{await get_last_entry()}🗣"
        list_channel = await ctx.guild.create_text_channel(channel_name, category=discord.utils.get(ctx.guild.categories, id=account_listing_category))

        transcript_channel = discord.utils.get(ctx.guild.text_channels, id=transcript_channel_id)
        await transcript_channel.send(
            f"{ctx.author.mention} listed the account `{username}` for `{price}` in {list_channel.mention}")
        data[0]["show_ign"] = show_ign
        data[0]["price"] = price
        data[0]["payment_methods"] = payment_methods
        data[0]["seller_id"] = ctx.user.id
        if show_ign:
            embed_title = f"Account Information for {data[0]['username']}"
            show_ign_embed = f"IGN: {data[0]['username']} | Listed by: <@{data[0]['seller_id']}>"
            embed_title_url = f"https://sky.shiiyu.moe/stats/{username}"
        else:
            show_ign_embed = f"Listed by: <@{data[0]['seller_id']}>"
            embed_title = "Account Information"
            embed_title_url = None
        embed = discord.Embed(
            title=embed_title,
            description="",
            color=color,
            url=embed_title_url
        )
        background = Editor(f"images/blank_1000.png")
        if "ADMIN" in data[0]["rank"]:
            rank = Editor(f"images/admin_rank.png").resize((975, 225))
        elif "YOUTUBE" in data[0]["rank"]:
            rank = Editor(f"images/youtube_rank.png").resize((975, 225))
        elif "SUPERSTAR" in data[0]["rank"]:
            rank = Editor(f"images/mvp++_rank.png").resize((975, 225))
        elif "MVP+" in data[0]["rank"]:
            rank = Editor(f"images/mvp+_rank.png").resize((975, 225))
        elif "MVP" in data[0]["rank"]:
            rank = Editor(f"images/mvp_rank.png").resize((975, 225))
        elif "VIP+" in data[0]["rank"]:
            rank = Editor(f"images/vip+_rank.png").resize((975, 225))
        elif "VIP" in data[0]["rank"]:
            rank = Editor(f"images/vip_rank.png").resize((975, 225))
        else:
            rank = Editor(f"images/non_rank.png").resize((975, 225))

        background.paste(rank, (0, 387))

        thumbnail = discord.File(fp=background.image_bytes, filename="rank.png")
        embed.add_field(name=f"{emojis_json['skillAverage']} Skill Average", value=f"{data[0]['skillAverage']}")
        embed.add_field(name=f"{emojis_json['catacombs']} Catacombs", value=f"{data[0]['dungeonLevel']}")
        embed.add_field(name=f"{emojis_json['weight']} Weight", value=f"{data[0]['weight']}")
        embed.add_field(name=f"{emojis_json['skyblockLevel']} SkyBlock Level:", value=f"{data[0]['skyblockLevel']}", inline=True)
        embed.add_field(name=f"{emojis_json['slayer']} Slayer",
                        value=f"{data[0]['zombie']} / {data[0]['spider']} / {data[0]['wolf']} / {data[0]['enderman']} / {data[0]['blaze']} / {data[0]['vampire']}")
        embed.add_field(name=f"{emojis_json['networthBank']} Networth:",
                        value=f"{data[0]['networth']} (Soulbound: {data[0]['soulboundNetworth']}) - Coins: {data[0]['coins']}",
                        inline=False)
        embed.add_field(name=f"{emojis_json['hotm']} HOTM",
                        value=f"{emojis_json['hotmLevel']} HOTM Level: {data[0]['hotmLevel']}\n{emojis_json['mithrilPowder']} Mithril Powder: {data[0]['mithrilPowder']}\n{emojis_json['gemstonePowder']} Gemstone Powder: {data[0]['gemstonePowder']}",
                        inline=True)
        embed.add_field(name=f"{emojis_json['crimsonIsle']} Crimson Isle",
                        value=f"{emojis_json['faction']} Faction: {data[0]['faction']}\n{emojis_json['mageRep']} Mage rep: {data[0]['mages_reputation']}\n{emojis_json['barbRep']} Barbarian rep: {data[0]['barbarians_reputation']}", inline=True)
        embed.add_field(name=f"❗ Extra Stats:", value=f"{show_ign_embed}", inline=False)
        embed.add_field(name="Price & Payment Methods", value=f"{price} | {payment_methods}", inline=False)
        embed.set_thumbnail(url=f"attachment://{thumbnail.filename}")
        sent_message = await list_channel.send(f"<@&{acc_ping_role}>", embed=embed, file=thumbnail, view=listingButtons(self.bot, data[0]["uuid"]))
        await insert_in_db(price, data[0]["uuid"], list_channel.id, sent_message.id, ctx.author.name, ctx.author.id, data[0], data[1], data[2])
        await ctx.edit(content="Successfully listed your account!")


def setup(bot):
    bot.add_cog(listing(bot))
