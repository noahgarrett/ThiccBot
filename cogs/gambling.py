import discord
from discord.ext import commands, tasks
import random
import main

class Gambling(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="coinflip", help=".coinflip (heads or tails) (bet amount)")
    async def coinflip(self, ctx, pick, bet_amt):
        bot_pick = random.randint(1, 2)
        users = await main.get_bank_data()
        user = ctx.author
        bank_amt = users[str(user.id)]["bank"]
        if int(bet_amt) <= bank_amt:
            if pick == 'heads' or pick == 'Heads' or pick == 'h' or pick == 'H':
                user_pick = 1
                if user_pick == bot_pick:
                    await main.bet_win(ctx.author, bet_amt)
                    await ctx.send(f'The coin chose **Heads**! You have doubled your bet of ${bet_amt}')
                else:
                    await main.bet_lose(ctx.author, bet_amt)
                    await ctx.send(f'The coin chose **Tails**! You have sadly lost your bet of ${bet_amt}')
            elif pick == 'tails' or pick == 'Tails' or pick == 't' or pick == 'T':
                user_pick = 2
                if user_pick == bot_pick:
                    await main.bet_win(ctx.author, bet_amt)
                    await ctx.send(f'The coin chose **Tails**! You have doubled your bet of ${bet_amt}')
                else:
                    await main.bet_lose(ctx.author, bet_amt)
                    await ctx.send(f'The coin chose **Heads**! You have sadly lost your bet of ${bet_amt}')
            else:
                await ctx.send('Please enter Heads or Tails')
        else:
            await ctx.send(f"You do not have enough funds for this bet. Your current balance is **${bank_amt}**")

    @commands.command(name="dice", help=".dice (over/under 50) (bet amount)")
    async def dice(self, ctx, pick, bet_amt):
        bot_pick = random.randint(0, 100)
        users = await main.get_bank_data()
        user = ctx.author
        bank_amt = users[str(user.id)]["bank"]
        if int(bet_amt) <= bank_amt:
            if pick == "over" or pick == "Over" or pick == "o" or pick == "O":
                if bot_pick >= 50:
                    await main.bet_win(ctx.author, bet_amt)
                    await ctx.send(
                        f"The magical dice rolled a **{bot_pick}**! You have doubled your bet of **${bet_amt}**")
                else:
                    await main.bet_lose(ctx.author, bet_amt)
                    await ctx.send(
                        f"The not so magical dice rolled a **{bot_pick}**... You have sadly lost your bet of **${bet_amt}**.")
            elif pick == "under" or pick == "Under" or pick == "u" or pick == "U":
                if bot_pick <= 50:
                    await main.bet_win(ctx.author, bet_amt)
                    await ctx.send(
                        f"The magical dice rolled a **{bot_pick}**! You have doubled your bet of **${bet_amt}**")
                else:
                    await main.bet_lose(ctx.author, bet_amt)
                    await ctx.send(
                        f"The not so magical dice rolled a **{bot_pick}**... You have sadly lost your bet of **${bet_amt}**.")
            else:
                await ctx.send("Please ender Over or Under")
        else:
            await ctx.send(f"You do not have enough funds for this bet. Your current balance is **${bank_amt}**")

def setup(client):
    client.add_cog(Gambling(client))