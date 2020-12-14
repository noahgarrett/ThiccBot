import discord
from discord.ext import commands, tasks
from discord.utils import get
import asyncio
import youtube_dl
from random import choice
import os, json, random
import main

class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.command(name="balance", help="Checks your account balance")
    async def balance(self, ctx):
        await main.open_account(ctx.author)

        user = ctx.author
        users = await main.get_bank_data()

        bank_amt = users[str(user.id)]["bank"]

        em = discord.Embed(
            title=f"{ctx.author.name}'s Account",
            description=f"{ctx.guild.name}'s Bank",
            color=discord.Color.red())
        em.add_field(name="Balance", value=f'${bank_amt}')
        await ctx.send(embed=em)

def setup(client):
    client.add_cog(Economy(client))