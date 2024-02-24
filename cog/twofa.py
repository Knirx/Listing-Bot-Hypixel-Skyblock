import discord, os, pyotp, time, datetime, asyncio
from discord import slash_command, Option
from discord.ext import commands
from main import bot

color = int(os.getenv("color"), 16)


class twoFa(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.slash_command(name="2fa")
    async def _2fa(self, ctx: discord.ApplicationContext,
                   secret: Option(str, "Enter the 2fa code that is given")):
        await ctx.defer(ephemeral=True)

        base32_secret = secret.upper().replace(" ", "")
        totp = pyotp.TOTP(base32_secret)
        key = totp.now()
        current_time = int(time.time())
        time_until_next_update = 30 - (current_time % 30)
        timestamp_until_update = time_until_next_update + current_time
        embed = discord.Embed(
            title="2FA Code",
            description=f"Update in: **<t:{timestamp_until_update}:R>**\n\n```{key}```",
            color=color
        )
        await ctx.edit(embed=embed)
        updates = 0
        while updates <= 3:
            current_time2 = int(time.time())
            time_until_next_update2 = 30 - (current_time2 % 30)

            if time_until_next_update2 == 29:
                key2 = totp.now()
                timestamp_until_update2 = time_until_next_update2 + current_time2
                embed2 = discord.Embed(
                    title="2FA Code",
                    description=f"Update in: **<t:{timestamp_until_update2}:R>**\n\n```{key2}```",
                    color=color
                )
                await ctx.edit(embed=embed2)
                updates += 1
            else:
                await asyncio.sleep(1)


def setup(bot):
    bot.add_cog(twoFa(bot))