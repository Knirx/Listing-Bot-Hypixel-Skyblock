import discord, os, asyncio, aiohttp
from discord.ext import commands, tasks
from discord import Option
from main import bot
from discord import Webhook

vouch_channel_id = int(os.getenv("vouch_channel"))

class resendVouches(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.slash_command()
    async def resend_vouch_data(self, ctx: discord.ApplicationContext, webhook_url: Optio(str, f"Enter the webhook you want to send the vouches to!")):
        await ctx.respond("Sending vouches ig", ephemeral=True)
        async with aiosqlite.connect(f'data/database.db') as db:
            async with db.execute('SELECT author_id, seller_id, review, avatar_url FROM vouches') as cursor:
                rows = await cursor.fetchall()

            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(webhook_url, session=session)

                for row in rows:
                    author_id, seller_id, review, avatar_url = row
                    author = ctx.guild.get_member(author_id)
                    embed = discord.Embed(
                        title=f"Vouch",
                        description=f"**Review:** <@{seller_id}> {review}\n\n**Voucher's ID:** {author_id}",
                        colour=color
                    )
                    try:
                        await webhook.send(embed=embed, avatar_url=f"{avatar_url}",
                                           username=f"{author.name}")
                    except discord.HTTPException:
                        continue
                    await asyncio.sleep(1.00005)

        async with aiosqlite.connect(f'data/database.db') as db2:
            async with db2.execute(
                    'SELECT author_id, author_name, author_pfp, message_content, img_urls FROM all_vouches') as cursors:
                rowss = await cursors.fetchall()

            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(webhook_url, session=session)

                for rowz in rowss:
                    author_id, author_name, author_pfp, message_content, img_urls = rowz
                    if message_content is None and img_urls is None:
                        continue
                    elif author_pfp is None:
                        author_pfp = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSClOZJUSUynXbZDD_miHXp1tTQ10IjdmI1tOYwf4dwBQ&s"
                    if img_urls is None:
                        embed = discord.Embed(
                            title=f"Vouch",
                            description=f"**Review:** {message_content}\n\n**Voucher's ID:** {author_id}",
                            colour=color
                        )
                        try:
                            await webhook.send(embed=embed, avatar_url=f"{author_pfp}",
                                               username=f"{author_name}")
                        except discord.HTTPException:
                            continue
                    else:
                        await webhook.send(content=f"{img_urls} {message_content}",
                                           avatar_url=f"https://cdn.discordapp.com/avatars/874304997096034335/a540ed25e5a1339e3779d4c14d7c8d8d.webp?size=1024",
                                           username=f"I am black")
                    await asyncio.sleep(1.00005)


def setup(bot):
    bot.add_cog(GetVouches(bot))
