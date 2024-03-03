import discord, json, PIL, easy_pil, aiosqlite, os
from other.request_data import *
from discord import Option
from discord.ext import commands
from bot import bot
from PIL import Image
from easy_pil import Editor, load_image_async, Font
from other.listing_view import EmbedView


load_dotenv(".env")
color = int(os.getenv("color"), 16)
account_listing_category = int(os.getenv("account_listing_category"))
transcript_channel_id = int(os.getenv("transcript_channel_id"))
acc_ping_role = int(os.getenv("acc_ping_role"))
profile_listing_category = int(os.getenv("profile_listing_category"))

with open("data/emojis.json") as emojis_json_file:
    emojis_json = json.load(emojis_json_file)
    emojis_json_file.close()


with open("data/emojisV3.json", 'r') as file:
    emoji_data = json.load(file)

async def get_last_entry():
    async with aiosqlite.connect(f"data/database.db") as db:
        async with db.execute("SELECT id FROM profile_listing ORDER BY id DESC LIMIT 1") as cursor:
            second_last_entry = await cursor.fetchone()
            if second_last_entry is None:
                second_last_entry = (0,)
            last_entry = second_last_entry[0] + 1
            return last_entry


async def insert_into_db(uuid, price, channel_id, message_id, author_name, author_id, skyhelper_response, hypixel_response):
    async with aiosqlite.connect(f"data/database.db") as db:
        await db.execute(
            "INSERT INTO profile_listing (uuid, price, channel_id, message_id, author_name, author_id, skyhelper_data, hypixel_data) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (uuid, price, channel_id, message_id, author_id, author_name, json.dumps(skyhelper_response), json.dumps(hypixel_response),))
        await db.commit()


class profile_listing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.has_permissions(administrator=True)
    @commands.slash_command()
    async def list_profile(self, ctx: discord.ApplicationContext,
                           username: Option(str, f"Enter a username"),
                           price: Option(str, f"Enter a price (numbers only)"),
                           payment_methods: Option(str, f"Enter all Payment options"),
                           show_ign: bool):

        await ctx.respond("Listing your profile! ||meow||", ephemeral=True)

        uuid = get_uuid(username)
        profile_request = get_main_profile_and_index(uuid)
        data = profile_request[1]
        skyhelper = get_skyhelper_data_only(uuid)


        if "$" in price:
            pass
        else:
            price = f"${price}"

        category = discord.utils.get(ctx.guild.categories, id=profile_listing_category)
        list_channel = await ctx.guild.create_text_channel(f"💲{price.replace('$', '')}｜profile-{await get_last_entry()}🗣", category=category)
        transcript_channel = discord.utils.get(ctx.guild.text_channels, id=transcript_channel_id)
        await transcript_channel.send(
            f"{ctx.author.mention} listed the profile `{username}` for `{price}`USD in {list_channel.mention}")
        networth = get_networth_with_types(skyhelper)
        networth["show_ign"] = show_ign
        networth["price"] = price
        networth["payment_methods"] = payment_methods
        networth["seller_id"] = ctx.user.id

        highest_tier = 0
        for entry in data["community_upgrades"]["upgrade_states"]:
            if entry["upgrade"] == "minion_slots":
                highest_tier += 1

        total_minion_slots = 0
        for member_id, member_data in data["members"].items():
            if "crafted_generators" in member_data["player_data"].keys():
                generators_data = member_data["player_data"]["crafted_generators"]
                total_minion_slots += len(generators_data)

        combined_dict = {}
        collections_datas = get_collection_data()
        for members_id, members_data in data["members"].items():
            try:
                members_datas = members_data["collection"].items()
            except KeyError:
                continue
            for item_name, item_value in members_datas:
                if item_name in combined_dict:
                    combined_dict[item_name] += item_value
                else:
                    combined_dict[item_name] = item_value
        total = 0
        for collection_type, collection_data in collections_datas["collections"].items():
            for name, items in collection_data["items"].items():
                for item_namez, item_valuez in combined_dict.items():
                    if item_namez == name:
                        tiers_list = items["tiers"]
                        for tier_data in tiers_list:
                            if item_valuez >= tier_data["amountRequired"]:
                                maxCollections = tier_data["tier"]
                                maxTiers = items["maxTiers"]
                                if maxCollections == maxTiers:
                                    total += 1

        hypixel_crafted_minions = get_minion_slots(total_minion_slots)
        hypixel_total_minions = highest_tier + hypixel_crafted_minions

        if show_ign:
            embed_title = skyhelper["username"]
            embed_url = f"https://sky.shiiyu.moe/stats/{username}"
        else:
            embed_title = "Someone"
            embed_url = None
        embed = discord.Embed(
            title=f"{embed_title}'s Profile",
            description=f"{emojis_json['networthBank']} Networth: **{networth['networth']} (Soulbound: {networth['soulboundNetworth']}) - Coins: {networth['coins']}**",
            color=color,
            url=embed_url
        )
        embed.add_field(name=f"{emojis_json['networthPurse']} Purse", value=f"**{networth['purse']}**")
        embed.add_field(name=f"{emojis_json['networthBank']} Bank", value=f"**{networth['bank']}**")
        for skyhelper_key, skyhelper_value in networth.items():
            if skyhelper_key.startswith("SKYHELPER_TYPES_"):
                embed.add_field(name=f"{emojis_json[skyhelper_key]} {skyhelper_key.replace('SKYHELPER_TYPES_', '').capitalize()}", value=f"**{skyhelper_value}**")
        embed.add_field(name=f"", value=f"")
        embed.add_field(name=f"{emojis_json['collections']} Collections:\nMaxed: {total} / {get_number_of_collections()}", value=f"")
        embed.add_field(name=f"{emojis_json['minions']} Total Minion Slots: {hypixel_total_minions}",
                        value=f"Crafted Minions: **{hypixel_crafted_minions}**\nCommunity Upgrade: **{highest_tier}** / 5")
        embed.add_field(name=f"{emojis_json['tickets_buy']} Price & Payment Methods",
                        value=f"{price} | {payment_methods}", inline=False)
        networth["total_collections"] = total
        networth["hypixel_total_minions"] = hypixel_total_minions
        networth["hypixel_crafted_minions"] = hypixel_crafted_minions
        networth["highest_tier"] = highest_tier
        sent_message = await list_channel.send(f"<@&{acc_ping_role}>", embed=embed, view=EmbedView(self.bot, uuid))
        await insert_into_db(uuid, price, list_channel.id, sent_message.id, ctx.author.name, ctx.author.id, networth, profile_request)


def setup(bot):
    bot.add_cog(profile_listing(bot))
