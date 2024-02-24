import discord, os
from discord.ext import commands
# TIC TAC TOE GAME WITH BUTTONS
color = int(os.getenv("color"), 16)
class TicTacToe(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="ttt", description="Play a game of TTT!")
    async def ttt(self, ctx, user: discord.Member):
        await ctx.respond(content=f"{user.mention}, {ctx.user.mention} challenged you to a game of Tic Tac Toe!",
                          view=ButtonRow(ctx.author, user))


class ButtonRow(discord.ui.View):
    def __init__(self, user, opponent):
        super().__init__(timeout=None)
        self.user = user
        self.opponent = opponent
        self.list = []
        self.winning = {
            "a": [["b", "c"], ["d", "g"], ["e", "i"], ["c", "b"], ["g", "d"], ["i", "e"]],
            "b": [["a", "c"], ["e", "h"], ["c", "a"], ["h", "e"]],
            "c": [["a", "b"], ["e", "g"], ["f", "i"], ["b", "a"], ["g", "e"], ["i", "f"]],
            "d": [["a", "g"], ["e", "f"], ["g", "a"], ["f", "e"]],
            "e": [["a", "i"], ["b", "h"], ["c", "g"], ["d", "f"], ["i", "a"], ["h", "b"], ["g", "c"], ["f", "d"]],
            "f": [["c", "i"], ["d", "e"], ["i", "c"], ["e", "d"]],
            "g": [["a", "d"], ["c", "e"], ["h", "i"], ["d", "a"], ["e", "c"], ["i", "h"]],
            "h": [["b", "e"], ["g", "i"], ["e", "b"], ["i", "g"]],
            "i": [["a", "e"], ["c", "f"], ["g", "h"], ["e", "a"], ["f", "c"], ["h", "g"]]
        }
        self.winning_2 = {
            "A": [["B", "C"], ["D", "G"], ["E", "I"], ["C", "B"], ["G", "D"], ["I", "E"]],
            "B": [["A", "C"], ["E", "H"], ["C", "A"], ["H", "E"]],
            "C": [["A", "B"], ["E", "G"], ["F", "I"], ["B", "A"], ["G", "E"], ["I", "F"], ["A", "B"]],
            "D": [["A", "G"], ["E", "F"], ["G", "A"], ["F", "E"]],
            "E": [["A", "I"], ["B", "H"], ["C", "G"], ["D", "F"], ["I", "A"], ["H", "B"], ["G", "C"], ["F", "D"]],
            "F": [["C", "I"], ["D", "E"], ["I", "C"], ["E", "D"]],
            "G": [["A", "D"], ["C", "E"], ["H", "I"], ["D", "A"], ["E", "C"], ["I", "H"]],
            "H": [["B", "E"], ["G", "I"], ["E", "B"], ["I", "G"]],
            "I": [["A", "E"], ["C", "F"], ["G", "H"], ["E", "A"], ["F", "C"], ["H", "G"]],
        }

    def go_through_list(self):
        if len(self.list) % 2 == 0:
            return True
        else:
            return False

    def end_game(self):
        if int(len(self.list)) >= 9:
            for k in self.list:
                if k.islower():
                    for m in self.winning[k]:
                        meow = all(item in self.list for item in m)
                        if meow is True:
                            return "true"
                elif k.isupper():
                    for m in self.winning_2[k]:
                        meow = all(item in self.list for item in m)
                        if meow is True:
                            return "true"
            return "Tie"
        else:
            for k in self.list:
                if k.islower():
                    for m in self.winning[k]:
                        meow = all(item in self.list for item in m)
                        if meow is True:
                            return "true"
                elif k.isupper():
                    for m in self.winning_2[k]:
                        meow = all(item in self.list for item in m)
                        if meow is True:
                            return "true"
            return False

    async def logic_function(self, interaction, button, lower_latter, capital_latter):
        if interaction.user.id == self.user.id:
            if self.go_through_list():
                self.list.append(lower_latter)
                if self.end_game() == "true":
                    winner = 0
                    for buttons in self.children:
                        buttons.disabled = True
                    if interaction.user.id == self.opponent.id:
                        winner += self.user.id
                    else:
                        winner += self.opponent.id
                    win_embed = discord.Embed(
                        title="GG",
                        description=f"<@{interaction.user.id}>, GG you won the game against <@{winner}>!"
                                    f"\n\nFor a rematch use the /ttt command again!",
                        color=0x00ff00
                    )
                    await self.message.edit(embed=win_embed, view=self)

                elif self.end_game() == "Tie":
                    for buttons in self.children:
                        buttons.disabled = True
                    tie_embed = discord.Embed(
                        title="GG",
                        description=f"The game was a Tie!\n\nUse the /ttt command for a rematch!",
                        color=color
                    )
                    await self.message.edit(embed=tie_embed, view=self)

                button.style = discord.ButtonStyle.success
                button.disabled = True
                button.label = "⭕"
                await self.message.edit(view=self)
                try:
                    await interaction.response.defer()
                except:
                    pass
            else:
                await interaction.response.send_message("It's not your turn!", ephemeral=True)
        elif interaction.user.id == self.opponent.id:
            if not self.go_through_list():
                self.list.append(capital_latter)
                if self.end_game() == "true":
                    winner = 0
                    for buttons in self.children:
                        buttons.disabled = True
                    if interaction.user.id == self.opponent.id:
                        winner += self.user.id
                    else:
                        winner += self.opponent.id
                    win_embed = discord.Embed(
                        title="GG",
                        description=f"<@{interaction.user.id}>, GG you won the game against {self.opponent.mention}!"
                                    f"\n\nFor a rematch use the /ttt command again!",
                        color=0x00ff00
                    )
                    await self.message.edit(embed=win_embed, view=self)

                elif self.end_game() == "Tie":
                    for buttons in self.children:
                        buttons.disabled = True
                    tie_embed = discord.Embed(
                        title="It's a Tie!",
                        description=f"The game was a Tie!\n\nUse the /ttt command for a rematch!",
                        color=0x0000ff
                    )
                    await self.message.edit(embed=tie_embed, view=self)

                button.style = discord.ButtonStyle.danger
                button.disabled = True
                button.label = "❌"
                await self.message.edit(view=self)
                try:
                    await interaction.response.defer()
                except:
                    pass
            else:
                await interaction.response.send_message("It's not your turn!", ephemeral=True)
        else:
            await interaction.response.send_message("This is not your game, please start one yourself with /ttt!",
                                                    ephemeral=True)
            return

    @discord.ui.button(label="|", style=discord.ButtonStyle.gray, custom_id="1", row=1)
    async def button_callback(self, button, interaction):
        try:
            await self.logic_function(interaction, button, "a", "A")
        except Exception as e:
            print(e)
    @discord.ui.button(label="|", style=discord.ButtonStyle.gray, custom_id="2", row=1)
    async def callback_2(self, button, interaction):
        try:
            await self.logic_function(interaction, button, "b", "B")
        except Exception as e:
            print(e)
    @discord.ui.button(label="|", style=discord.ButtonStyle.gray, custom_id="3", row=1)
    async def callback_3(self, button, interaction):
        try:
            await self.logic_function(interaction, button, "c", "C")
        except Exception as e:
            print(e)
    @discord.ui.button(label="|", style=discord.ButtonStyle.gray, custom_id="4", row=2)
    async def callback_4(self, button, interaction):
        try:
            await self.logic_function(interaction, button, "d", "D")
        except Exception as e:
            print(e)
    @discord.ui.button(label="|", style=discord.ButtonStyle.gray, custom_id="5", row=2)
    async def callback_5(self, button, interaction):
        try:
            await self.logic_function(interaction, button, "e", "E")
        except Exception as e:
            print(e)
    @discord.ui.button(label="|", style=discord.ButtonStyle.gray, custom_id="6", row=2)
    async def callback_6(self, button, interaction):
        try:
            await self.logic_function(interaction, button, "f", "F")
        except Exception as e:
            print(e)
    @discord.ui.button(label="|", style=discord.ButtonStyle.gray, custom_id="7", row=3)
    async def callback_7(self, button, interaction):
        try:
            await self.logic_function(interaction, button, "g", "G")
        except Exception as e:
            print(e)
    @discord.ui.button(label="|", style=discord.ButtonStyle.gray, custom_id="8", row=3)
    async def callback_8(self, button, interaction):
        try:
            await self.logic_function(interaction, button, "h", "H")
        except Exception as e:
            print(e)
    @discord.ui.button(label="|", style=discord.ButtonStyle.gray, custom_id="9", row=3)
    async def callback_9(self, button, interaction):
        try:
            await self.logic_function(interaction, button, "i", "I")
        except Exception as e:
            print(e)

def setup(bot):
    bot.add_cog(TicTacToe(bot))
