import discord, os, asyncio, aiosqlite
from discord import Option
from discord.ext import commands, tasks
from dotenv import load_dotenv
from other.listing_view import listingButtons, ticket_delete_button
from cog.tickets import TicketsView
from bot import bot

load_dotenv(".env")
token = os.getenv("bot_token")
owner_id = int(os.getenv("bot_owner_id"))
command_prefix = os.getenv("cmd_prefix")
vouch_channel_id = int(os.getenv("vouch_channel"))
color = int(os.getenv("color"), 16)
intents = discord.Intents.all()
owner_ids_array = [1174704996999233598, 1103236001410863145]


async def database_stuff():
    async with aiosqlite.connect(f"data/database.db") as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS listing (
                id INTEGER PRIMARY KEY,
                uuid STRING,
                price INTEGER,
                channel_id INTEGER,
                message_id INTEGER,
                author_name STRING,
                author_id INTEGER,
                data TEXT
                );""")
        await db.execute("""CREATE TABLE IF NOT EXISTS vouches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                author_id INTEGER,
                seller_id INTEGER,
                review TEXT,
                avatar_url TEXT
                );""")
        await db.execute("""CREATE TABLE IF NOT EXISTS all_vouches (
                        author_id INTEGER,
                        author_name STRING,
                        author_pfp STRING,
                        message_content STRING,
                        img_urls STRING
                );""")
        await db.execute("""CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                LTC STRING,
                BTC STRING,
                ETH STRING,
                paypal STRING,
                venmo STRING,
                cashapp STRING,
                zelle STRING
                );""")
        await db.commit()


async def update_listing_view():
    async with aiosqlite.connect(f"data/database.db") as db:
        async with db.execute("SELECT * FROM listing") as c:
            async for result in c:
                uuid = result[1]
                message_id = result[4]
                try:
                    channel = await bot.fetch_channel(result[3])
                except:
                    async with db.execute("BEGIN"):
                        await db.execute("DELETE FROM listing WHERE uuid = ?", (uuid,))
                        await db.commit()
                        continue
                try:
                    message = await channel.fetch_message(message_id)
                except:
                    async with db.execute("BEGIN"):
                        await db.execute("DELETE FROM listing WHERE uuid = ?", (uuid,))
                        await db.commit()
                        continue
                await message.edit(view=listingButtons(bot, uuid))



@bot.event
async def on_ready():
    bot.add_view(ticket_delete_button(bot))
    bot.add_view(TicketsView())
    await database_stuff()
    await update_listing_view()
    print(f"Logged in as {bot.user}")
    await get_vouches_loop.start()


@tasks.loop(hours=12)
async def get_vouches_loop():
    channel = bot.get_channel(vouch_channel_id)
    if channel is None:
        print("Vouch channel not found.")
        return

    async with aiosqlite.connect("data/database.db") as db:
        await db.execute("DELETE FROM all_vouches")
        await db.commit()

    async for message in channel.history(limit=None):
        if message.author.bot:
            continue

        message_content = message.content
        author_name = message.author.name
        author_id = message.author.id
        author_pfp = str(message.author.avatar)

        attachment_urls = [attachment.url for attachment in message.attachments]
        if attachment_urls:
            for url in attachment_urls:
                async with aiosqlite.connect("data/database.db") as db:
                    await db.execute(
                        "INSERT INTO all_vouches (author_id, author_name, author_pfp, message_content, img_urls) VALUES (?, ?, ?, ?, ?)",
                        (author_id, author_name, author_pfp, message_content, url))
                    await db.commit()
        else:
            async with aiosqlite.connect("data/database.db") as db:
                await db.execute(
                    "INSERT INTO all_vouches (author_id, author_name, author_pfp, message_content, img_urls) VALUES (?, ?, ?, ?, ?)",
                    (author_id, author_name, author_pfp, message_content, None))
                await db.commit()

@bot.event
async def on_message(message):
    content = message.content
    if content.strip() == f"{command_prefix}payments":
        embed = discord.Embed(
            title=f"Payment methods of ***{message.guild.name}***",
            description=f"",
            color=color
        )
        embed.set_thumbnail(url=f"{message.guild.icon}")
        async with aiosqlite.connect(f"data/database.db") as db2:
            async with db2.execute("SELECT user_id, LTC, BTC, ETH, paypal, venmo, cashapp, zelle FROM payments") as cursor:
                meow = await cursor.fetchall()
                entries = len(meow) - 1
                while entries >= 0:
                    user_id = meow[entries][0]
                    LTC = meow[entries][1]
                    BTC = meow[entries][2]
                    ETH = meow[entries][3]
                    paypal = meow[entries][4]
                    venmo = meow[entries][5]
                    cashapp = meow[entries][6]
                    zelle = meow[entries][7]
                    entries -= 1
                    embed.add_field(name="",
                                    value=f"***<@{user_id}>'s \nPayment methods!***\n\n\n***LTC***: `{LTC}`"
                                          f"\n***BTC***: `{BTC}`\n***ETH***: `{ETH}`\n***PayPal***: `{paypal}`\n"
                                          f"***CashApp***: `{cashapp}`\n***Venmo***: `{venmo}`\n"
                                          f"***Zelle***: `{zelle}`")
            await db2.commit()
        await message.reply(embed=embed)

    elif f"{command_prefix}payments " in message.content.lower():
        try:
            splited_content = content.split(" ")[1]
            if splited_content.startswith("<@"):
                real_id = splited_content[2:-1]
            else:
                real_id = splited_content
            user = await bot.fetch_user(real_id)
            embed = discord.Embed(
                title=f"",
                description=f"",
                color=color
            )
            embed.set_thumbnail(url=f"{user.avatar}")
            async with aiosqlite.connect(f"data/database.db") as db2:
                async with db2.execute(
                        "SELECT user_id, LTC, BTC, ETH, paypal, venmo, cashapp, zelle FROM payments WHERE user_id = ?", (real_id, )) as cursor:
                    fetched_data = await cursor.fetchone()
                    if fetched_data:
                        user_id = fetched_data[0]
                        LTC = fetched_data[1]
                        BTC = fetched_data[2]
                        ETH = fetched_data[3]
                        paypal = fetched_data[4]
                        venmo = fetched_data[5]
                        cashapp = fetched_data[6]
                        zelle = fetched_data[7]
                        embed.add_field(name="",
                                        value=f"***<@{user_id}>'s \nPayment methods!***\n\n\n***LTC***: `{LTC}`"
                                              f"\n***BTC***: `{BTC}`\n***ETH***: `{ETH}`\n***PayPal***: `{paypal}`\n"
                                              f"***CashApp***: `{cashapp}`\n***Venmo***: `{venmo}`\n"
                                              f"***Zelle***: `{zelle}`")
                await db2.commit()
            await message.reply(embed=embed)
        except:
            await message.reply("The user you mentioned might not be in the database, make sure they have permission to use /payment_methods!")




for files in os.listdir("cog"):
    if files.endswith(".py"):
        bot.load_extension(f"cog.{files[:-3]}")

if __name__ == "__main__":
    bot.run(token)

