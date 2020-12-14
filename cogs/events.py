import discord
from discord.ext import commands, tasks

class Events(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(activity=discord.Game("w/ My pp"))
        print("Bot is online.")
        print(f'Discord.PY Version: {discord.__version__}')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        print(f'{member} has joined a server.')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        print(f'{member} has left a server.')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Please use .help for the correct arguments')

def setup(client):
    client.add_cog(Events(client))
