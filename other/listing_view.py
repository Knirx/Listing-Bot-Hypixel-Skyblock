import discord, json, PIL, easy_pil, io, os, chat_exporter, requests, aiosqlite
from other.request_data import *
from other.calcs import *
from discord import Option
from discord.ext import commands
from bot import bot
from PIL import Image
from io import BytesIO
from easy_pil import Editor, load_image_async, Font
from dotenv import load_dotenv

load_dotenv(".env")
token = os.getenv("API_KEY")
color = int(os.getenv("color"), 16)
buy_acc_category = int(os.getenv("buy_acc_category"))
seller_role_id = int(os.getenv("seller_role_id"))
transcript_channel_id = int(os.getenv("transcript_channel_id"))
buy_profile_category_id = int(os.getenv("buy_profile_category_id"))


with open("data/emojis.json") as emojis_json_file:
    emojis_json = json.load(emojis_json_file)
    emojis_json_file.close()

with open("data/itemHash.json", "r") as item_hashs:
    item_hashes = json.load(item_hashs)

with open("data/emojisV3.json", 'r') as file:
    emoji_data = json.load(file)


class ticket_delete_button(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="Delete Ticket", style=discord.ButtonStyle.red, emoji="🔒",
                       custom_id="button_5")
    async def button_callback(self, button, interaction):
        channel = interaction.guild.get_channel(transcript_channel_id)

        await interaction.response.send_message("Closing Ticket...")

        transcript = await chat_exporter.export(
            channel=interaction.channel,
            limit=None,
            bot=self.bot
        )

        file = discord.File(
            io.BytesIO(transcript.encode()),
            filename="Transcript.html"
        )

        channel_message = await channel.send(file=file)
        link = await chat_exporter.link(channel_message)
        embed = discord.Embed(
            title="Ticket closed!",
            description=f"",
            url=link,
            color=color
        )
        embed.add_field(name="Ticket name:", value=f"{interaction.channel.name}")
        embed.add_field(name="", value="")
        embed.add_field(name="Ticket closed by:", value=f"{interaction.user.mention}")
        embed.add_field(name="", value=f"**[Transcript]({link})**\n\nYou can find the Transcript **[here!]({link})**")

        await channel.send(embed=embed)
        await interaction.channel.delete()


class listingButtons(discord.ui.View):
    def __init__(self, bot, uuid, message=None):
        super().__init__(timeout=None)
        self.bot = bot
        self.message = message
        self.uuid = uuid
        self.main_profile = get_main_profile(self.uuid)
        self.skyhelper = requests.get(f"http://{host}/v1/profiles/{self.uuid}?key={skyhelper_key}").json()["data"][0]
        self.skyhelper_data = get_networth(self.skyhelper)

    options = [
        discord.SelectOption(label='Buy', description='Buy the account', emoji='🎫', value='2351'),
        discord.SelectOption(label="Networth", description="Networth Breakdown", emoji=f"{emojis_json['networthBank']}", value="654"),
        discord.SelectOption(label='Skills', description='Skills', emoji=f'{emojis_json["skillAverage"]}',
                             value='231'),
        discord.SelectOption(label='Dungeons', description='Dungeon Stats', emoji=f'{emojis_json["catacombs"]}',
                             value='213'),
        discord.SelectOption(label='Slayer', description='Slayer Stats', emoji=f'{emojis_json["slayer"]}',
                             value='312'),
        discord.SelectOption(label='Crimson Isle', description='Crimson Isle Stats',
                             emoji=f'{emojis_json["crimsonIsle"]}', value='4123')]

    async def select_data_from_db(self, uuid):
        async with aiosqlite.connect("data/database.db") as db:
            async with db.execute("SELECT data FROM listing WHERE uuid = ?", (uuid,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    row_0 = row[0]
                    json_load = json.loads(row_0)
                    return json_load
                else:
                    return None

    @discord.ui.select(
        max_values=1,
        placeholder='Click to buy or view Account stats!',
        options=options,
        custom_id='6969429'
    )

    async def callback(self, select, interaction):
        if select.values[0] == "2351":
            ticket_channel = await interaction.guild.create_text_channel(f'buy-{interaction.user.name}',
                category=discord.utils.get(interaction.guild.categories, id=buy_acc_category))
            await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True,
                                                 view_channel=True)
            await ticket_channel.set_permissions(interaction.guild.default_role, view_channel=False)
            await interaction.response.send_message(f"New channel created at {ticket_channel.mention}", ephemeral=True)
            data = await self.select_data_from_db(self.uuid)
            if data is not None:
                if data["show_ign"] is True:
                    embed_title = f"Account Information for {data['username']}"
                    show_ign_embed = f"IGN: {data['username']} | Listed by: <@{data['seller_id']}>"
                    embed_title_url = f"https://sky.shiiyu.moe/stats/{data['username']}"
                else:
                    show_ign_embed = f"Listed by: <@{data['seller_id']}>"
                    embed_title = "Account Information"
                    embed_title_url = None
                embed = discord.Embed(
                    title=embed_title,
                    description="",
                    color=color,
                    url=embed_title_url
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
                embed.add_field(name=f"{emojis_json['skyblockLevel']} SkyBlock Level:",
                                value=f"{data['skyblockLevel']}", inline=True)
                embed.add_field(name=f"{emojis_json['slayer']} Slayer",
                                value=f"{data['zombie']} / {data['spider']} / {data['wolf']} / {data['enderman']} / {data['blaze']} / {data['vampire']}")
                embed.add_field(name=f"{emojis_json['networthBank']} Networth:",
                                value=f"{data['networth']} (Soulbound: {data['soulboundNetworth']}) - Coins: {data['coins']}",
                                inline=False)
                embed.add_field(name=f"{emojis_json['hotm']} HOTM",
                                value=f"{emojis_json['hotmLevel']} HOTM Level: \n{emojis_json['mithrilPowder']} Mithril Powder: {data['mithrilPowder']}\n{emojis_json['gemstonePowder']} Gemstone Powder: {data['gemstonePowder']}",
                                inline=True)
                embed.add_field(name=f"{emojis_json['crimsonIsle']} Crimson Isle",
                                value=f"{emojis_json['faction']} Faction: {data['faction']}\n{emojis_json['mageRep']} Mage rep: {data['mages_reputation']}\n{emojis_json['barbRep']} Barbarian rep: {data['barbarians_reputation']}",
                                inline=True)
                embed.add_field(name=f"❗ Extra Stats:", value=f"{show_ign_embed}", inline=False)
                embed.add_field(name="Price & Payment Methods", value=f"{data['price']} | {data['payment_methods']}", inline=False)
                embed.set_thumbnail(url=f"attachment://{thumbnail.filename}")
                sent_message = await ticket_channel.send(f"<@&{seller_role_id}>", embed=embed, file=thumbnail,
                                                       view=ticket_delete_button(self.bot))

        if select.values[0] == "654":
            await interaction.response.defer()

            net_worth_by_category = {}
            category_items = {}

            for types, help in self.skyhelper["networth"]["types"].items():
                if types in ["essence", "sacks", "museum", "potion_bag", "fishing_bag", "personal_vault",
                             "candy_inventory"]:
                    continue

                category_total_value = 0
                category_items[types.capitalize()] = []

                for names in help["items"]:
                    soulbound = names["soulbound"]
                    if soulbound is False:
                        value = names["price"]
                        category_total_value += value
                        category_items[types.capitalize()].append({
                            "name": f'{names["name"]}',
                            "value": format_TBMK(value),
                        })
                        net_worth_by_category[types.capitalize()] = category_total_value

            embed = discord.Embed(
                title="*Someone's* Networth",
                description=f"{emojis_json['networthBank']} Networth: **{self.skyhelper_data['networth']}** (Coins: **{self.skyhelper_data['coins']}**) Soulbound: **{self.skyhelper_data['unsoulboundNetworth']}**",
                color=color,
            )

            for section in category_items.keys():
                total_value = format_TBMK(net_worth_by_category.get(section, 0))

                embed.add_field(
                    name=f"{section} ({total_value})",
                    value="\n".join(
                        [f"{item['name']} ({item['value']})" for item in category_items.get(section, [])[:4]]),
                    inline=False
                )

            await interaction.followup.send(embed=embed, ephemeral=True, view=self)

        if select.values[0] == "231":
            skills_data = get_skills_overflow(self.main_profile)
            embed = discord.Embed(
                title="Skill Breakdown:",
                color=color
            )
            for skill_key, skill_value in skills_data.items():
                if skill_key.startswith("SKILL_"):
                    emoji = emojis_json[f"{skill_key.replace('SKILL_', '').lower()}"]
                    embed.add_field(name=f"{emoji} {skill_key.replace('SKILL_', '').capitalize()}:", value=f"{skill_value}")
            await interaction.response.send_message(embed=embed, ephemeral=True, view=self)

        if select.values[0] == "213":
            embed = discord.Embed(
                title="Dungeon Breakdown",
                color=color
            )

            for dg_type in ["catacombs", "master_catacombs"]:
                for i in range(1, 8):
                    if dg_type == "catacombs":
                        embed.add_field(name=f"{emojis_json[f'{i}_dungeon_completions']} Floor {i} runs:", value=f'{self.main_profile["dungeons"]["dungeon_types"][f"{dg_type}"]["tier_completions"][f"{i}"]}')
                    else:
                        embed.add_field(name=f"{emojis_json[f'{i}_dungeon_completions']} Master {i} runs:", value=f'{self.main_profile["dungeons"]["dungeon_types"][f"{dg_type}"]["tier_completions"][f"{i}"]}')

            total_levels = 0
            for klass, exp in self.main_profile["dungeons"]["player_classes"].items():
                level_exp = dungeon_cless_level(exp['experience'])
                embed.add_field(name=f"{emojis_json[klass]} {klass.capitalize()} Class Level:", value=f"{level_exp}")
                total_levels += level_exp
            embed.add_field(name="Class Average:", value=f"{emojis_json['dungeon_class_average']} {(total_levels/5):.2f}")
            await interaction.response.send_message(embed=embed, ephemeral=True, view=self)

        if select.values[0] == "312":
            embed = discord.Embed(
                title="Slayer Breakdown",
                color=color
            )

            for slayer_key, slayer_value in self.main_profile["slayer"]["slayer_bosses"].items():
                embed.add_field(name=f"{emojis_json[slayer_key]} {slayer_key.capitalize()} Slayer:", value=f"{get_slayer_lvl_with_overflow_exp(slayer_key, slayer_value['xp'])}")
            await interaction.response.send_message(embed=embed, ephemeral=True, view=self)

        if select.values[0] == "4123":
            embed = discord.Embed(
                title="Crimson Isle Breakdown",
                color=color
            )

            for kuudra_key, kuudra_value in self.main_profile["nether_island_player_data"]["kuudra_completed_tiers"].items():
                if "_" in kuudra_key:
                    continue
                if kuudra_key == "none":
                    embed.add_field(name=f"{emojis_json['basic']} Basic Kuudra Completions:", value=f"{kuudra_value}")
                else:
                    embed.add_field(name=f"{emojis_json[kuudra_key]} {kuudra_key.capitalize()} Kuudra Completions:", value=f"{kuudra_value}")

            for dojo_key, dojo_value in self.main_profile["nether_island_player_data"]["dojo"].items():
                if "time" in dojo_key:
                    continue
                embed.add_field(name=f"{emojis_json[dojo_key]} {dojo_key.replace('dojo_points_', '').replace('_', ' ').capitalize()}", value=f"{dojo_value}")

            await interaction.response.send_message(embed=embed, ephemeral=True, view=self)


class EmbedView(discord.ui.View):
    def __init__(self, bot, uuid):
        super().__init__(timeout=None)
        self.bot = bot
        self.uuid = uuid

    async def select_data_from_db(self, uuid):
        async with aiosqlite.connect("data/database.db") as db:
            async with db.execute("SELECT skyhelper_data, hypixel_data FROM profile_listing WHERE uuid = ?", (uuid,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    row_0 = row[0]
                    row_1 = row[1]
                    json_load = json.loads(row_0)
                    json_load_1 = json.loads(row_1)
                    return [json_load, json_load_1]
                else:
                    return None

    @discord.ui.button(label="Buy", style=discord.ButtonStyle.gray, emoji="🎫",
                       custom_id="buy_ticket_button")

    async def button_callback(self, button, interaction):
        channel_mention = interaction.channel.mention
        category123 = discord.utils.get(interaction.guild.categories, id=buy_profile_category_id)
        ticket_channel = await interaction.guild.create_text_channel(f'buy-{interaction.user.name}',
                                                                     category=category123)
        await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True,
                                             view_channel=True)
        await ticket_channel.set_permissions(interaction.guild.default_role, view_channel=False)
        await interaction.response.send_message(f"New channel created at {ticket_channel.mention}", ephemeral=True)

        data = await self.select_data_from_db(self.uuid)
        networth = data[0]

        if data is not None:
            if networth["show_ign"] is True:
                embed_title = networth['username']
                embed_url = f"https://sky.shiiyu.moe/stats/{networth['username']}"
            else:
                embed_title = f"Someone"
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
                    embed.add_field(
                        name=f"{emojis_json[skyhelper_key]} {skyhelper_key.replace('SKYHELPER_TYPES_', '').capitalize()}",
                        value=f"**{skyhelper_value}**")
            embed.add_field(name=f"", value=f"")
            embed.add_field(name=f"{emojis_json['collections']} Collections:\nMaxed: {networth['total_collections']} / {get_number_of_collections()}", value=f"")
            embed.add_field(name=f"{emojis_json['minions']} Total Minion Slots: {networth['hypixel_total_minions']}",
                            value=f"Crafted Minions: **{networth['hypixel_crafted_minions']}**\nCommunity Upgrade: **{networth['highest_tier']}** / 5")
            embed.add_field(name=f"{emojis_json['tickets_buy']} Price & Payment Methods",
                            value=f"{networth['price']} | {networth['payment_methods']}", inline=False)
            await ticket_channel.send(f"<@&{seller_role_id}> {interaction.user.mention} {channel_mention}", embed=embed, view=ticket_delete_button(self.bot))

    @discord.ui.button(label="Extra Stats", style=discord.ButtonStyle.gray, emoji="📊",
                       custom_id="nw_button", row=0)
    async def button2_callback(self, button, interaction):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(
            title="Extra Stats",
            url="",
            colour=color,
            description="Click the select menu below to view extra stats!"
        )

        await interaction.followup.send(embed=embed, ephemeral=True, view=NetworthView(self.uuid))



class NetworthView(discord.ui.View):
    def __init__(self, uuid):
        super().__init__(timeout=None)
        self.bot = bot
        self.uuid = uuid
        self.skyhelper_raw_data = get_skyhelper_data_only(uuid)
        self.skyhelper = get_networth(self.skyhelper_raw_data)
        self.category_emote_mapping = {
            "Armor": f"{emojis_json['SKYHELPER_TYPES_armor']}",
            "Equipment": f"{emojis_json['SKYHELPER_TYPES_equipment']}",
            "Wardrobe": f"{emojis_json['SKYHELPER_TYPES_wardrobe']}",
            "Inventory": f"{emojis_json['SKYHELPER_TYPES_inventory']}",
            "Enderchest": f"{emojis_json['SKYHELPER_TYPES_enderchest']}",
            "Accessories": f"{emojis_json['SKYHELPER_TYPES_accessories']}",
            "Storage": f"{emojis_json['SKYHELPER_TYPES_storage']}",
            "Pets": f"{emojis_json['SKYHELPER_TYPES_pets']}",
        }

    optionz = [
        discord.SelectOption(label='Networth', description='Networth Breakdown', emoji=f'{emojis_json["networthBank"]}', value='58391'),
        discord.SelectOption(label='Unsoulbound Networth', description='Unsoulbound Networth Breakdown', emoji='💸', value='58392'),
        discord.SelectOption(label='Collections', description='All Collections', emoji=f'{emojis_json["carpentry"]}', value='987'),
    ]

    @discord.ui.select(
        max_values=1,
        placeholder="Click here to select a option",
        options=optionz,
        custom_id="7585"
    )
    async def callback(self, select, interaction):
        if select.values[0] == "58391":
            await interaction.response.defer()

            net_worth_by_category = {}
            category_items = {}

            for types, types_value in self.skyhelper_raw_data["networth"]["types"].items():
                if types in ["essence", "sacks", "museum", "potion_bag", "fishing_bag", "personal_vault",
                             "candy_inventory"]:
                    continue

                category_total_value = 0
                category_items[types.capitalize()] = []

                for items in types_value["items"]:
                    value = items["price"]
                    category_total_value += items["price"]

                    category_items[types.capitalize()].append({
                        "name": f'{items["name"]}',
                        "value": format_TBMK(value),
                    })

                    net_worth_by_category[types.capitalize()] = category_total_value

            embed = discord.Embed(
                title="*Someone's* Networth",
                description=f"{emojis_json['networthBank']} Networth: **{self.skyhelper['networth']}** (Coins: **{self.skyhelper['coins']}**) Soulbound: **{self.skyhelper['soulboundNetworth']}**",
                color=color,
            )

            for section in category_items.keys():
                total_value = format_TBMK(net_worth_by_category.get(section, 0))
                emote_name = self.category_emote_mapping.get(section, "default_emote")
                emote = f"{emote_name}"

                embed.add_field(
                    name=f"{emote} {section} ({total_value})",
                    value="\n".join(
                        [f"{item['name']} ({item['value']})" for item in category_items.get(section, [])[:4]]),
                    inline=False
                )

            await interaction.edit_original_response(embed=embed, view=self)

        elif select.values[0] == "58392":

            await interaction.response.defer()
            net_worth_by_category = {}
            category_items = {}
            for types, types_value in self.skyhelper_raw_data["networth"]["types"].items():
                if types in ["essence", "sacks", "museum", "potion_bag", "fishing_bag", "personal_vault",
                             "candy_inventory"]:
                    continue

                category_total_value = 0
                category_items[types.capitalize()] = []

                for items in types_value["items"]:
                    soulbound = items["soulbound"]
                    if soulbound is False:
                        value = items["price"]
                        category_total_value += value
                        category_items[types.capitalize()].append({
                            "name": f'{items["name"]}',
                            "value": format_TBMK(value),
                        })
                        net_worth_by_category[types.capitalize()] = category_total_value
                    else:
                        continue

            embed = discord.Embed(
                title="*Someone's* Networth",
                description=f"{emojis_json['networthBank']} Networth: **{self.skyhelper['networth']}** (Coins: **{self.skyhelper['coins']}**) Soulbound: **{self.skyhelper['unsoulboundNetworth']}**",
                color=color,
            )

            for section in category_items.keys():
                total_value = format_TBMK(net_worth_by_category.get(section, 0))
                emote_name = self.category_emote_mapping.get(section, "default_emote")
                emote = f"{emote_name}"

                embed.add_field(
                    name=f"{emote} {section} ({total_value})",
                    value="\n".join(
                        [f"{item['name']} ({item['value']})" for item in category_items.get(section, [])[:4]]),
                    inline=False
                )

            await interaction.edit_original_response(embed=embed, view=self)

        elif select.values[0] == "987":
            await interaction.response.defer()

            embed = discord.Embed(
                title=f"Collection Breakdown",
                description=f"Click the select menu below to view collection breakdowns",
                color=color
            )

            await interaction.followup.send(embed=embed, ephemeral=True, view=NetworthView2(self.uuid, self.skyhelper_raw_data, self.skyhelper))


class NetworthView2(discord.ui.View):
    def __init__(self, uuid, skyhelper_all, skyhelper):
        super().__init__(timeout=None)
        self.bot = bot
        self.uuid = uuid
        self.skyhelper_raw_data = skyhelper_all
        self.skyhelper = skyhelper
        self.hypixel = get_main_profile_and_index(self.uuid)
        self.collection_data = get_collection_data()


    optionzs = [
        discord.SelectOption(label='Farming', description='Farming collections', emoji=f'{emojis_json["farming"]}', value='987654'),
        discord.SelectOption(label='Mining', description='Mining collections', emoji=f'{emojis_json["mining"]}', value='876'),
        discord.SelectOption(label='Combat', description='Combat collections', emoji=f'{emojis_json["combat"]}', value='765'),
        discord.SelectOption(label='Foraging', description='Foraging collections', emoji=f'{emojis_json["foraging"]}', value='654'),
        discord.SelectOption(label='Fishing', description='Fishing collections', emoji=f'{emojis_json["fishing"]}>', value='456'),
        discord.SelectOption(label='Rift', description='Rift collections', emoji=f'{emojis_json["rift"]}', value='567'),
    ]

    @discord.ui.select(
        max_values=1,
        placeholder="Click here to select a option",
        options=optionzs,
        custom_id="758566"
    )

    async def callback(self, select, interaction):
        if select.values[0] == "987654":
            await interaction.response.defer()
            maxCollections = 0
            combined_dict = {}
            collection_name = None
            data = self.hypixel[1]
            for members_id, members_data in data["members"].items():
                try:
                    members_datas = data["members"][members_id]["collection"].items()
                except KeyError:
                    continue
                for item_name, item_value in members_datas:
                    if item_name in combined_dict:
                        combined_dict[item_name] += item_value
                    else:
                        combined_dict[item_name] = item_value

            max_tiers = 0
            item_valuezz = 0
            max_tierz = 0
            maxTiers = 0
            collection_info_dict = {}

            for name, items in self.collection_data["collections"]["FARMING"]["items"].items():
                for item_namez, item_valuez in combined_dict.items():
                    if item_namez == name and item_valuez >= items["maxTiers"]:
                        item_valuezz = item_valuez
                        tiers_list = items["tiers"]
                        for tier_data in tiers_list:
                            if item_valuezz >= tier_data["amountRequired"]:
                                maxCollections = tier_data["tier"]
                                maxTiers = items["maxTiers"]
                                collection_name = items["name"]
                                if maxCollections == maxTiers:
                                    max_tierz += 1
                                    max_tiers = "yes"
                                else:
                                    max_tiers = "no"

                    elif item_namez == name:
                        tiers_list = items["tiers"]
                        for tier_data in tiers_list:
                            if item_valuezz >= tier_data["amountRequired"]:
                                maxCollections = tier_data["tier"]
                                maxTiers = items["maxTiers"]
                                collection_name = items["name"]
                                if maxCollections == maxTiers:
                                    max_tierz += 1
                                    max_tiers = "yes"
                                else:
                                    max_tiers = "no"
                formatted_number = format_TBMK(item_valuezz)

                collection_info_dict[collection_name] = {
                    "name": collection_name,
                    "level": maxCollections,
                    "collection": formatted_number,
                    "maxed?": max_tiers,
                    "max": maxTiers,
                }

            embed = discord.Embed(
                title=f"Farming Collection Breakdown",
                description=f"**Maxed Collections: {max_tierz}/17**",
                color=color,
            )

            for collection_name, collection_data in collection_info_dict.items():
                embed.add_field(
                    name=f"",
                    value=f"**{collection_name}** Level: **{collection_data['level']}** / {collection_data['max']} (`{collection_data['collection']}`)",
                    inline=False
                )

            if interaction.message:
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True, view=self)

        elif select.values[0] == "876":
            await interaction.response.defer()
            maxCollections = 0
            combined_dict = {}
            collection_name = None
            data = self.hypixel[1]

            for members_id, members_data in data["members"].items():
                try:
                    members_datas = data["members"][members_id]["collection"].items()
                except KeyError:
                    continue
                for item_name, item_value in members_datas:
                    if item_name in combined_dict:
                        combined_dict[item_name] += item_value
                    else:
                        combined_dict[item_name] = item_value
            max_tiers = 0
            item_valuezz = 0
            max_tierz = 0
            maxTiers = 0
            collection_info_dict = {}
            for name, items in self.collection_data["collections"]["MINING"]["items"].items():
                for item_namez, item_valuez in combined_dict.items():
                    if item_namez == name and item_valuez >= items["maxTiers"]:
                        item_valuezz = item_valuez
                        tiers_list = items["tiers"]
                        for tier_data in tiers_list:
                            if item_valuezz >= tier_data["amountRequired"]:
                                maxCollections = tier_data["tier"]
                                maxTiers = items["maxTiers"]
                                collection_name = items["name"]
                                if maxCollections == maxTiers:
                                    max_tierz += 1
                                    max_tiers = "yes"
                                else:
                                    max_tiers = "no"

                    elif item_namez == name:
                        tiers_list = items["tiers"]
                        for tier_data in tiers_list:
                            if item_valuezz >= tier_data["amountRequired"]:
                                maxCollections = tier_data["tier"]
                                maxTiers = items["maxTiers"]
                                collection_name = items["name"]
                                if maxCollections == maxTiers:
                                    max_tierz += 1
                                    max_tiers = "yes"
                                else:
                                    max_tiers = "no"
                formatted_number = format_TBMK(item_valuezz)

                collection_info_dict[collection_name] = {
                    "name": collection_name,
                    "level": maxCollections,
                    "collection": formatted_number,
                    "maxed?": max_tiers,
                    "max": maxTiers,
                }
            embed = discord.Embed(
                title=f"Farming Collection Breakdown",
                description=f"**Maxed Collections: {max_tierz}/22**",
                color=color,
            )


            for collection_name, collection_data in collection_info_dict.items():
                embed.add_field(
                    name=f"",
                    value=f"**{collection_name}** Level: **{collection_data['level']}** / {collection_data['max']} (`{collection_data['collection']}`)",
                    inline=False
                )

            if interaction.message:
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True, view=self)


        elif select.values[0] == "765":

            await interaction.response.defer()
            maxCollections = 0
            combined_dict = {}
            collection_name = None
            data = self.hypixel[1]

            for members_id, members_data in data["members"].items():
                try:
                    members_datas = data["members"][members_id]["collection"].items()
                except KeyError:
                    continue

                for item_name, item_value in members_datas:
                    if item_name in combined_dict:
                        combined_dict[item_name] += item_value
                    else:
                        combined_dict[item_name] = item_value


            max_tiers = 0
            item_valuezz = 0
            max_tierz = 0
            maxTiers = 0
            collection_info_dict = {}

            for name, items in self.collection_data["collections"]["COMBAT"]["items"].items():
                for item_namez, item_valuez in combined_dict.items():
                    if item_namez == name and item_valuez >= items["maxTiers"]:
                        item_valuezz = item_valuez
                        tiers_list = items["tiers"]
                        for tier_data in tiers_list:
                            if item_valuezz >= tier_data["amountRequired"]:
                                maxCollections = tier_data["tier"]
                                maxTiers = items["maxTiers"]
                                collection_name = items["name"]
                                if maxCollections == maxTiers:
                                    max_tierz += 1
                                    max_tiers = "yes"
                                else:
                                    max_tiers = "no"

                    elif item_namez == name:
                        tiers_list = items["tiers"]
                        for tier_data in tiers_list:
                            if item_valuezz >= tier_data["amountRequired"]:
                                maxCollections = tier_data["tier"]
                                maxTiers = items["maxTiers"]
                                collection_name = items["name"]
                                if maxCollections == maxTiers:
                                    max_tierz += 1
                                    max_tiers = "yes"
                                else:
                                    max_tiers = "no"
                formatted_number = format_TBMK(item_valuezz)


                collection_info_dict[collection_name] = {
                    "name": collection_name,
                    "level": maxCollections,
                    "collection": formatted_number,
                    "maxed?": max_tiers,
                    "max": maxTiers,
                }
            embed = discord.Embed(
                title=f"Farming Collection Breakdown",
                description=f"**Maxed Collections: {max_tierz}/11**",
                color=color,
            )

            for collection_name, collection_data in collection_info_dict.items():
                embed.add_field(
                    name=f"",
                    value=f"**{collection_name}** Level: **{collection_data['level']}** / {collection_data['max']} (`{collection_data['collection']}`)",
                    inline=False
                )

            if interaction.message:
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True, view=self)

        elif select.values[0] == "654":
            await interaction.response.defer()

            maxCollections = 0
            combined_dict = {}
            collection_name = None
            data = self.hypixel[1]

            for members_id, members_data in data["members"].items():
                try:
                    members_datas = data["members"][members_id]["collection"].items()
                except KeyError:
                    continue

                for item_name, item_value in members_datas:
                    if item_name in combined_dict:
                        combined_dict[item_name] += item_value
                    else:
                        combined_dict[item_name] = item_value


            max_tiers = 0
            item_valuezz = 0
            max_tierz = 0
            maxTiers = 0
            collection_info_dict = {}

            for name, items in self.collection_data["collections"]["FORAGING"]["items"].items():
                for item_namez, item_valuez in combined_dict.items():
                    if item_namez == name and item_valuez >= items["maxTiers"]:
                        item_valuezz = item_valuez
                        tiers_list = items["tiers"]
                        for tier_data in tiers_list:
                            if item_valuezz >= tier_data["amountRequired"]:
                                maxCollections = tier_data["tier"]
                                maxTiers = items["maxTiers"]
                                collection_name = items["name"]
                                if maxCollections == maxTiers:
                                    max_tierz += 1
                                    max_tiers = "yes"
                                else:
                                    max_tiers = "no"

                    elif item_namez == name:
                        tiers_list = items["tiers"]
                        for tier_data in tiers_list:
                            if item_valuezz >= tier_data["amountRequired"]:
                                maxCollections = tier_data["tier"]
                                maxTiers = items["maxTiers"]
                                collection_name = items["name"]
                                if maxCollections == maxTiers:
                                    max_tierz += 1
                                    max_tiers = "yes"
                                else:
                                    max_tiers = "no"
                formatted_number = format_TBMK(item_valuezz)


                collection_info_dict[collection_name] = {
                    "name": collection_name,
                    "level": maxCollections,
                    "collection": formatted_number,
                    "maxed?": max_tiers,
                    "max": maxTiers,
                }
            embed = discord.Embed(
                title=f"Farming Collection Breakdown",
                description=f"**Maxed Collections: {max_tierz}/6**",
                color=color,
            )

            for collection_name, collection_data in collection_info_dict.items():
                embed.add_field(
                    name=f"",
                    value=f"**{collection_name}** Level: **{collection_data['level']}** / {collection_data['max']} (`{collection_data['collection']}`)",
                    inline=False
                )

            if interaction.message:
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True, view=self)

        elif select.values[0] == "456":
            await interaction.response.defer()

            maxCollections = 0
            combined_dict = {}
            collection_name = None
            data = self.hypixel[1]

            for members_id, members_data in data["members"].items():
                try:
                    members_datas = data["members"][members_id]["collection"].items()
                except KeyError:
                    continue

                for item_name, item_value in members_datas:
                    if item_name in combined_dict:
                        combined_dict[item_name] += item_value
                    else:
                        combined_dict[item_name] = item_value

            max_tiers = 0
            item_valuezz = 0
            max_tierz = 0
            maxTiers = 0
            collection_info_dict = {}

            for name, items in self.collection_data["collections"]["FISHING"]["items"].items():
                for item_namez, item_valuez in combined_dict.items():
                    if item_namez == name and item_valuez >= items["maxTiers"]:
                        item_valuezz = item_valuez
                        tiers_list = items["tiers"]
                        for tier_data in tiers_list:
                            if item_valuezz >= tier_data["amountRequired"]:
                                maxCollections = tier_data["tier"]
                                maxTiers = items["maxTiers"]
                                collection_name = items["name"]
                                if maxCollections == maxTiers:
                                    max_tierz += 1
                                    max_tiers = "yes"
                                else:
                                    max_tiers = "no"

                    elif item_namez == name:
                        tiers_list = items["tiers"]
                        for tier_data in tiers_list:
                            if item_valuezz >= tier_data["amountRequired"]:
                                maxCollections = tier_data["tier"]
                                maxTiers = items["maxTiers"]
                                collection_name = items["name"]
                                if maxCollections == maxTiers:
                                    max_tierz += 1
                                    max_tiers = "yes"
                                else: 
                                    max_tiers = "no"
                formatted_number = format_TBMK(item_valuezz)


                collection_info_dict[collection_name] = {
                    "name": collection_name,
                    "level": maxCollections,
                    "collection": formatted_number,
                    "maxed?": max_tiers,
                    "max": maxTiers,
                }
            embed = discord.Embed(
                title=f"Fishing Collection Breakdown",
                description=f"**Maxed Collections: {max_tierz}/11**",
                color=color,
            )

            for collection_name, collection_data in collection_info_dict.items():
                embed.add_field(
                    name=f"",
                    value=f"**{collection_name}** Level: **{collection_data['level']}** / {collection_data['max']} (`{collection_data['collection']}`)",
                    inline=False
                )

            if interaction.message:
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True, view=self)


        elif select.values[0] == "567":
            await interaction.response.defer()

            maxCollections = 0
            combined_dict = {}
            collection_name = None
            data = self.hypixel[1]

            for members_id, members_data in data["members"].items():
                try:
                    members_datas = data["members"][members_id]["collection"].items()
                except KeyError:
                    continue

                for item_name, item_value in members_datas:
                    if item_name in combined_dict:
                        combined_dict[item_name] += item_value
                    else:
                        combined_dict[item_name] = item_value


            max_tiers = 0
            item_valuezz = 0
            max_tierz = 0
            maxTiers = 0
            collection_info_dict = {}

            for name, items in self.collection_data["collections"]["RIFT"]["items"].items():
                for item_namez, item_valuez in combined_dict.items():
                    if item_namez == name and item_valuez >= items["maxTiers"]:
                        item_valuezz = item_valuez
                        tiers_list = items["tiers"]
                        for tier_data in tiers_list:
                            if item_valuezz >= tier_data["amountRequired"]:
                                maxCollections = tier_data["tier"]
                                maxTiers = items["maxTiers"]
                                collection_name = items["name"]
                                if maxCollections == maxTiers:
                                    max_tierz += 1
                                    max_tiers = "yes"
                                else:
                                    max_tiers = "no"

                    elif item_namez == name:
                        tiers_list = items["tiers"]
                        for tier_data in tiers_list:
                            if item_valuezz >= tier_data["amountRequired"]:
                                maxCollections = tier_data["tier"]
                                maxTiers = items["maxTiers"]
                                collection_name = items["name"]
                                if maxCollections == maxTiers:
                                    max_tierz += 1
                                    max_tiers = "yes"
                                else:
                                    max_tiers = "no"
                formatted_number = format_TBMK(item_valuezz)


                collection_info_dict[collection_name] = {
                    "name": collection_name,
                    "level": maxCollections,
                    "collection": formatted_number,
                    "maxed?": max_tiers,
                    "max": maxTiers,
                }
            embed = discord.Embed(
                title=f"Rift Collection Breakdown",
                description=f"**Maxed Collections: {max_tierz}/6**",
                color=color,
            )

            for collection_name, collection_data in collection_info_dict.items():
                embed.add_field(
                    name=f"",
                    value=f"**{collection_name}** Level: **{collection_data['level']}** / {collection_data['max']} (`{collection_data['collection']}`)",
                    inline=False
                )

            if interaction.message:
                await interaction.edit_original_response(embed=embed, view=self)
            else:
                await interaction.response.send_message(embed=embed, ephemeral=True, view=self)
