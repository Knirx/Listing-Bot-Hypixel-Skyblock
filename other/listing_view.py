import discord, json, PIL, easy_pil, io, os, chat_exporter, requests, aiosqlite
from other.request_data import *
from other.calcs import *
from discord import Option
from discord.ext import commands
from other.idk_what_this_is import bot
from PIL import Image
from io import BytesIO
from easy_pil import Editor, load_image_async, Font
from dotenv import load_dotenv

load_dotenv(".env")
token = os.getenv("API_KEY")
color = int(os.getenv("color"), 16)
buy_acc_category = int(os.getenv("buy_acc_category"))
seller_role_id = int(os.getenv("seller_role_id"))

with open("data/emojis.json") as emojis_json_file:
    emojis_json = json.load(emojis_json_file)
    emojis_json_file.close()

with open("data/itemHash.json", "r") as item_hashs:
    item_hashes = json.load(item_hashs)

with open("data/emojisV3.json", 'r') as file:
    emoji_data = json.load(file)


class ticket_delete_button(discord.ui.View):
    def __init__(self):
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
    def __init__(self, uuid, message=None):
        super().__init__(timeout=None)
        self.bot = bot
        self.message = message
        self.uuid = uuid
        self.main_profile = get_main_profile(self.uuid)
        self.skyhelper = requests.get(f"http://{host}/v1/profiles/{self.uuid}?key=knax").json()["data"][0]
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
                                                       view=ticket_delete_button())


                #meow = await ticket_channel.send(f"<@&{seller_role_id}> {interaction.user.mention} {interaction.channel.mention}", embed=self.embed, view=ticketCloseButton(acc_id))
                # print(self.message, self.message.embeds)
                # await self.send_embed_to_channel(self.message, ticket_channel, new_content=f"<@&{seller_role_id}>",
                                                 # new_view=ticket_delete_button())

        if select.values[0] == "654":

            await interaction.response.defer()

            item_hash_value = ""
            value = 0
            net_worth_by_category = {}
            category_items = {}
            #print(data)

            for types, help in self.skyhelper["networth"]["types"].items():
                if types in ["essence", "sacks", "museum", "potion_bag", "fishing_bag", "personal_vault",
                             "candy_inventory"]:
                    continue

                category_total_value = 0
                category_items[types.capitalize()] = []

                for names in help["items"]:
                    soulbound = names["soulbound"]

                    if "type" in names:
                        if soulbound is False:
                            idz = names["type"]
                            value = names["price"]
                            category_total_value += value
                            if idz in item_hashes.keys():
                                item_hash_value = item_hashes[idz]

                    elif "id" in names:
                        if soulbound is False:
                            id = names["id"].upper()
                            value = names["price"]
                            category_total_value += value
                            if id in item_hashes.keys():
                                item_hash_value = item_hashes[id]

                    if item_hash_value in emoji_data:
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


