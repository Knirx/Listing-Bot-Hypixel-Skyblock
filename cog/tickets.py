import discord, json, PIL, easy_pil, os, io, chat_exporter, requests, aiosqlite
from other.request_data import *
from other.calcs import *
from discord import Option, slash_command
from discord.ext import commands
from bot import bot
from other.listing_view import ticket_delete_button
from PIL import Image
from io import BytesIO
from easy_pil import Editor, load_image_async, Font
from dotenv import load_dotenv

load_dotenv(".env")
color = int(os.getenv("color"), 16)
seller_role_id = int(os.getenv("seller_role_id"))
buy_coins_category = int(os.getenv("buy_coins_category"))
sell_coins_category = int(os.getenv("sell_coins_category"))
support_category = int(os.getenv("support_category"))
transcript_channel_id = int(os.getenv("transcript_channel_id"))
panel_channel = int(os.getenv("panel_channel"))
sell_acc_category = int(os.getenv("sell_acc_category"))

with open("data/emojis.json") as emojis_json_file:
    emojis_json = json.load(emojis_json_file)
    emojis_json_file.close()


class BuyCoinTickets(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Info", timeout=None)
        self.bot = bot

        self.ign_input = discord.ui.InputText(placeholder="(ex. 56ms)", label="What's your IGN?", max_length=16)
        self.coins_input = discord.ui.InputText(placeholder="(ex. 500m)",
                                                label="How many coins would you like to sell?", max_length=6)
        self.payment_input = discord.ui.InputText(placeholder="(ex. Paypal, LTC, BTC,...)",
                                                  label="How would you like to get paid?", max_length=10)
        self.add_item(self.ign_input)
        self.add_item(self.coins_input)
        self.add_item(self.payment_input)


    async def callback(self, interaction):
        await interaction.response.defer(ephemeral=True)
        if not self.children[1].value.isalpha() or self.children[1].value.lower() not in ('m', 'b'):
            value_input = self.children[1].value
            if value_input.isdigit():
                value_input += "000000" and "m"
            elif 'b' and ',' in value_input or 'b' and '.' in value_input:
                pass

            _03rate = 0.00000003 * convert_to_int_with_letters(value_input)
            _02rate = 0.00000002 * convert_to_int_with_letters(value_input)

            embed123 = discord.Embed(
                title="Ticket info",
                description=f"***`This ticket was opened by` <@{interaction.user.id}>!***",
                color=color
            )
            embed123.add_field(name="What's your IGN?", value=f"***`{self.children[0].value}`***", inline=False)
            embed123.add_field(name="How many coins would you like to sell?", value=f"***`{value_input}`***",
                               inline=False)
            embed123.add_field(name="How would you like to get paid?", value=f"***`{self.children[2].value}`***",
                               inline=False)
            embed123.add_field(name="Payment if coins:", value=f"***`{round(_03rate, 1)}$` at 0.03/m***", inline=True)
            embed123.add_field(name="Payment if items:", value=f"***`{round(_02rate, 1)}$` at 0.02/m***")

            category = discord.utils.get(interaction.guild.categories, id=sell_coins_category)
            formatted_value = convert_to_int_with_letters(value_input) * 0.0000001

            ticket_channel = await interaction.guild.create_text_channel(f'sell-{self.children[2].value}-{formatted_value}m',
                                                                         category=category)
            await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True,
                                                 view_channel=True)
            await ticket_channel.set_permissions(interaction.guild.default_role, view_channel=False)
            await interaction.followup.send(content=f"New channel created at {ticket_channel.mention}", ephemeral=True)
            meow = await ticket_channel.send(f"<@&{seller_role_id}>", embed=embed123, view=ticket_delete_button(self.bot))
            await meow.pin()


class SellCoinTickets(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Info", timeout=None)
        self.bot = bot

        self.ign_input = discord.ui.InputText(placeholder="(ex. 56ms)", label="What's your IGN?", max_length=16)
        self.coins_input = discord.ui.InputText(placeholder="(ex. 500m)",
                                                label="How many coins would you like to buy?", max_length=6)
        self.payment_input = discord.ui.InputText(placeholder="(ex. Paypal, LTC, BTC,...)",
                                                  label="How would you like to pay?", max_length=10)
        self.add_item(self.ign_input)
        self.add_item(self.coins_input)
        self.add_item(self.payment_input)


    async def callback(self, interaction):
        await interaction.response.defer()
        if not self.children[1].value.isalpha() or self.children[1].value.lower() not in ('m', 'b'):
            value_input = self.children[1].value
            if value_input.isdigit():
                value_input += "000000" and "m"
            elif 'b' and ',' in value_input or 'b' and '.' in value_input:
                pass

            _06rate = 0.00000006 * convert_to_int_with_letters(value_input)
            _05rate = 0.00000005 * convert_to_int_with_letters(value_input)

            embed123 = discord.Embed(
                title="Ticket info",
                description=f"***`This ticket was opened by` <@{interaction.user.id}>!***",
                color=color,
                url=f"https://sky.shiiyu.moe/stats/{self.children[0].value}"
            )
            embed123.add_field(name="What's your IGN?", value=f"***`{self.children[0].value}`***", inline=False)
            embed123.add_field(name="How many coins would you like to buy?", value=f"***`{value_input}`***", inline=False)
            embed123.add_field(name="How would you like to pay?", value=f"***`{self.children[2].value}`***",
                               inline=False)
            embed123.add_field(name="Price for coins:", value=f"***`{round(_06rate, 1)}$`*** at 0.06/m", inline=True)
            embed123.add_field(name="Price for items:", value=f"***`{round(_05rate, 1)}$`*** at 0.05/m")

            category = discord.utils.get(interaction.guild.categories, id=buy_coins_category)

            if 'b' and '.' or 'b' and ',' in self.children[1].value:
                formatted_value = convert_to_int_with_letters(value_input) * 0.0000001

                ticket_channel = await interaction.guild.create_text_channel(f'buy-{self.children[2].value}-{formatted_value}m',
                                                                             category=category)
                await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True,
                                                     view_channel=True)
                await ticket_channel.set_permissions(interaction.guild.default_role, view_channel=False)
                await interaction.followup.send(content=f"New channel created at <#{ticket_channel.id}>", ephemeral=True)
                meow = await ticket_channel.send(f"<@&{seller_role_id}>", embed=embed123, view=ticket_delete_button(self.bot))
                await meow.pin()


class SupportTickets(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Info", timeout=None)
        self.bot = bot

        self.ign_input = discord.ui.InputText(placeholder="USE KEYWORDS ONLY HERE ARE THE OPTIONS: SUPPORT | EXCHANGE | MIDDLEMAN", label="What do you need?", max_length=11, style=discord.InputTextStyle.long)
        self.amount_input = discord.ui.InputText(placeholder="(Use this field to describe your issue more, you can stop using keywords here!)", label="Describe your issue more!", max_length=4000, style=discord.InputTextStyle.long, required=False)
        self.add_item(self.ign_input)
        self.add_item(self.amount_input)

    async def callback(self, interaction):
        await interaction.response.defer()
        try:
            self.amount_input = self.children[1].value or "None"

            embed123 = discord.Embed(
                title="Ticket info",
                description=f"***`This ticket was opened by` <@{interaction.user.id}>!***",
                color=color
            )
            embed123.add_field(name="This ticket is for:", value=f"***`{self.children[0].value}`***", inline=False)
            embed123.add_field(name="Issue description:", value=self.amount_input, inline=False)

            category = discord.utils.get(interaction.guild.categories, id=support_category)
            ticket_channel = await interaction.guild.create_text_channel(f'{self.children[0].value}-{interaction.user.name}',
                                                                         category=category)
            await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True,
                                                 view_channel=True)
            await ticket_channel.set_permissions(interaction.guild.default_role, view_channel=False)
            await interaction.followup.send(content=f"New channel created at {ticket_channel.mention}", ephemeral=True)
            meow = await ticket_channel.send(f"<@&{seller_role_id}>", embed=embed123, view=ticket_delete_button(self.bot))
            await meow.pin()
        except:
            await interaction.followup.send(content="Something went wrong please contact the seller!")




class AccountTickets(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Info", timeout=None)
        self.bot = bot

        self.ign_input = discord.ui.InputText(placeholder="(ex. 56ms)", label="Whats the Account IGN?", max_length=16)
        self.coins_input = discord.ui.InputText(placeholder="(ex. $210)", label="How much do you want for your Account?", max_length=20)
        self.payment_input = discord.ui.InputText(placeholder="(ex. Paypal, LTC, BTC,...)", label="What payment methods can you take?", max_length=20)
        self.add_item(self.ign_input)
        self.add_item(self.coins_input)
        self.add_item(self.payment_input)

    async def callback(self, interaction):
        price = self.children[1].value
        username = self.children[0].value
        payment_methods = self.children[2].value

        await interaction.response.defer()
        data = get_all(username, False)[0]
        ticket_channel = await interaction.guild.create_text_channel(f'sell-${price}-{username}',
                                                                     category=discord.utils.get(interaction.guild.categories, id=sell_acc_category))
        await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True,
                                             view_channel=True)
        await ticket_channel.set_permissions(interaction.guild.default_role, view_channel=False)
        await interaction.followup.send(f"Ticket created at {ticket_channel.mention}", ephemeral=True)

        if "$" not in price:
            price = f"${price}"
        embed = discord.Embed(
            title=f"Account Information for {data['username']}",
            description="",
            color=color,
            url=f"https://sky.shiiyu.moe/stats/{username}"
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
        embed.add_field(name="Price & Payment Methods", value=f"{price} | {payment_methods}", inline=False)
        embed.set_thumbnail(url=f"attachment://{thumbnail.filename}")
        await ticket_channel.send(f"<@&{seller_role_id}>", embed=embed, file=thumbnail, view=ticket_delete_button(self.bot))

class TicketsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    options = [
        discord.SelectOption(label='Sell Account', description='Click here to sell an account!', emoji='🎫', value='1'),
        discord.SelectOption(label='Sell Coins', description='Click here to sell coins or items!',
                             emoji='<:coin:1140349985469255771>', value='2'),
        discord.SelectOption(label='Buy Coins', description='Click here to buy coins or items!',
                             emoji='<:dollar:1140350441255862416>', value='3'),
        discord.SelectOption(label='Support | Exchange | Middleman',
                             description='Click here for support, exchanges or Middleman!',
                             emoji='<:support:1139671363406286869>', value='4')
    ]

    @discord.ui.select(
        min_values=1,
        max_values=1,
        placeholder='Select a Ticket below',
        options=options,
        custom_id='TicketsView'
    )
    async def select_callback(self, select, interaction):
        if '1' in interaction.data['values']:
            await interaction.response.send_modal(AccountTickets())
        if '2' in interaction.data['values']:
            await interaction.response.send_modal(BuyCoinTickets())
        if '3' in interaction.data['values']:
            await interaction.response.send_modal(SellCoinTickets())
        if '4' in interaction.data['values']:
            await interaction.response.send_modal(SupportTickets())

class Ticket(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketsView())


    @slash_command()
    @commands.has_permissions(administrator=True)
    async def close(self, ctx: discord.ApplicationContext):
        channel = self.bot.get_channel(transcript_channel_id)

        required_role = discord.utils.get(ctx.author.roles, id=seller_role_id)
        if required_role:
            await ctx.defer()
            transcript = await chat_exporter.export(
                channel=ctx.channel,
                limit=None,
                bot=self.bot
            )

            file = discord.File(
                io.BytesIO(transcript.encode()),
                filename="Transcript.html"
            )

            msg = await channel.send(file=file)
            link = await chat_exporter.link(msg)

            embed = discord.Embed(
                title="Ticket closed via /close!",
                description=f"You can find the Transcript of {ctx.channel.name} [here!]({link})",
                url=link,
                color=color
            )
            embed.add_field(name="Ticket name:", value=f"{ctx.channel.name}", inline=True)
            embed.add_field(name="Ticket closed by:", value=f"{ctx.user.name}")
            await channel.send(embed=embed)
            await asyncio.sleep(1)
            await ctx.channel.delete()
        else:
            await ctx.respond("You have no perms to do this!", ephemeral=True)
            return

    @slash_command()
    @commands.has_permissions(administrator=True)
    async def tickets(self, ctx: discord.ApplicationContext):
        em = discord.Embed(
            title='Tickets',
            description=f'**WE SELL COINS FOR** ```0.06/m.```\n**WE SELL ITEMS FOR** ```0.05/m.```\n\n**WE BUY COINS FOR** ```0.03/m.```\n**WE BUY ITEMS FOR** ```0.02/m.```\n\n**HOWEVER THIS DEPENDS HIGHLY ON THE AMOUNT YOU SELL TO US**\n\n***WE ALSO BUY ACCOUNTS, OPEN A TICKET BELOW!***\n\n\n[🎫] For Sell Account\n\n[{emojis_json["tickets_sell"]}] For Sell Coins\n\n[{emojis_json["tickets_buy"]}] For Buy Coins\n\n[{emojis_json["tickets_support"]}] For Support',
            color=color
        )
        await ctx.send(embed=em, view=TicketsView())
        await ctx.respond(content="Sent!", ephemeral=True)


def setup(bot):
    bot.add_cog(Ticket(bot))