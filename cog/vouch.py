import discord, os, aiohttp, aiosqlite
from discord import slash_command, Option, Webhook
from discord.ext import commands
from bot import bot

color = int(os.getenv("color"), 16)
vouches_webhook = os.getenv("vouches_webhook")
vouch_role_id = int(os.getenv("vouch_role_id"))
class vouch(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command()
    async def vouch(self, ctx: discord.ApplicationContext,
                    seller: discord.Member,
                    review: Option(str, f"How would you review the seller and what did u buy or sell?")):
        url = vouches_webhook
        author_id = ctx.author.id
        avatar_url = str(ctx.author.avatar)

        if vouch_role_id not in [role.id for role in ctx.author.roles]:
            await ctx.respond("You don't have permissions to do that!", ephemeral=True)
        else:
            async with aiohttp.ClientSession() as session:
                webhook = Webhook.from_url(url, session=session)
                embed = discord.Embed(
                    title=f"Vouch",
                    description=f"**Seller:** {seller.mention}\n**Review:** {review}\n\n**Voucher's ID:** {ctx.author.id}",
                    colour=color
                )
                await webhook.send(embed=embed, username=f"{ctx.author.name}", avatar_url=f"{ctx.author.avatar}")
                await ctx.respond("Successfully vouched!", ephemeral=True)
                async with aiosqlite.connect(f"data/database.db") as db:
                    await db.execute('INSERT INTO vouches (author_id, seller_id, review, avatar_url) VALUES (?, ?, ?, ?)',
                                     (author_id, seller.id, review, avatar_url))
                    await db.commit()


def setup(bot):
    bot.add_cog(vouch(bot))