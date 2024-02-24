import aiosqlite, discord
from discord import Option, slash_command
from discord.ext import commands
from bot import bot


class paymentMethods(commands.Cog):
    def __int__(self, bot):
        self.bot = bot

    @commands.has_permissions(administrator=True)
    @commands.slash_command()
    async def payment_methods(self, ctx: discord.ApplicationContext,
                              ltc: Option(str, f"Enter your ltc addy"),
                              btc: Option(str, f"Enter your btc addy"),
                              eth: Option(str, f"Enter your eth addy"),
                              paypal: Option(str, f"Enter your eth addy", required=False),
                              venmo: Option(str, f"Enter your eth addy", required=False),
                              cashapp: Option(str, f"Enter your eth addy", required=False),
                              zelle: Option(str, f"Enter your eth addy", required=False)):
            async with aiosqlite.connect(f"data/database.db") as db:
                user_row = await db.execute("SELECT * FROM payments WHERE user_id = ?", (ctx.user.id,))
                existing_row = await user_row.fetchone()

                update_query = "UPDATE payments SET "
                update_values = []
                if existing_row:
                    if ltc:
                        update_query += "LTC=?, "
                        update_values.append(ltc)
                    if btc:
                        update_query += "BTC=?, "
                        update_values.append(btc)
                    if eth:
                        update_query += "ETH=?, "
                        update_values.append(eth)
                    if paypal:
                        update_query += "paypal=?, "
                        update_values.append(paypal)
                    if venmo:
                        update_query += "venmo=?, "
                        update_values.append(venmo)
                    if cashapp:
                        update_query += "cashapp=?, "
                        update_values.append(cashapp)
                    if zelle:
                        update_query += "zelle=?, "
                        update_values.append(zelle)
                    update_query = update_query.rstrip(", ") + " WHERE user_id = ?"
                    update_values.append(ctx.user.id)
                    await db.execute(update_query, update_values)
                else:
                    await db.execute(
                        "INSERT INTO payments (user_id, LTC, BTC, ETH, paypal, venmo, cashapp, zelle) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                        (ctx.user.id, ltc, btc, eth, paypal, venmo, cashapp, zelle))
                await db.commit()

                await ctx.respond("Saved your payment methods!", ephemeral=True)

def setup(bot):
    bot.add_cog(paymentMethods(bot))
