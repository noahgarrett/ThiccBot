import discord
from discord.ext import commands, tasks
from discord.utils import get
import asyncio
import youtube_dl
from random import choice
import os, json, random
import requests
from bs4 import BeautifulSoup

noah_path = "C:\\Users\\noahw\\Desktop\\Coding\\Github Projects\\ThiccBot\\venv"
cody_path = ""

os.chdir(noah_path)

client = commands.Bot(command_prefix = '.')
token = '{INSERT BOT TOKEN HERE}'

## Cog Commands ##
@client.command()
async def load(ctx, extension):
    client.load_extension(f'cogs.{extension}')

@client.command()
async def unload(ctx, extension):
    client.unload_extension(f'cogs.{extension}')

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')
        print(filename[:-3])
### Music Setup ###
music_queue = []
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0' # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

### Normal Commands ###
@client.command(name='ping', help='Shows the latency of the bot')
async def ping(ctx):
    await ctx.send(f"My latency is: {round(client.latency * 1000)}ms")

@client.command(name='clear', help='Clears 1-100 messages from a voice channel')
async def clear(ctx, amount = 5):
    if (amount == 0):
        await ctx.send("Why would you even do this command for zero messages... Try again")
    elif (amount > 100):
        await ctx.send("# of messages must be 100 or less at a time")
    else:
         await ctx.channel.purge(limit= amount)
         await ctx.send(f"Deleted {amount} messages.")

@client.command(name='geton', help='Tells a provided user to get the fuck on..')
async def geton(ctx, member: discord.Member, *, reason=None):
    i = 5
    while i > 0:
        i -= 1
        await ctx.send(f"Get the fuck on {member.mention}")

#@client.command()
#async def avatar(ctx): # Used to change Bot's avatar
    #filename = 'asa.jpg'
    #with open(filename, 'rb') as f:
        #image = f.read()
        #await client.user.edit(avatar=image)

#@client.command()
#async def rename(ctx, name):
    #await client.user.edit(username=name)

#@client.command()
#async def null(ctx):
    #user = ctx.author
    #role = discord.utils.get(ctx.guild.roles, name="Bots")
    #await discord.Member.add_roles(user, role)

#@client.command()
#async def null(ctx):
    #guild = ctx.guild
    #await guild.create_role(name='N-Word Pass', color=discord.Color.from_rgb(248, 24, 148), permissions=discord.Permissions(permissions=0x00000008))
### Helper Functions ###
async def get_bank_data():
    with open("mainbank.json", "r") as f:
        users = json.load(f)
    return users


async def open_account(user):
    users = await get_bank_data()

    if str(user.id) in users:
        return False
    else:
        users[str(user.id)] = {}
        users[str(user.id)]["bank"] = 100

    with open("mainbank.json", "w") as f:
        json.dump(users, f, indent=4)
    return True

async def bet_win(user, bet_amt):
    users = await get_bank_data()
    bank_amt = users[str(user.id)]["bank"]
    bet_double = int(bet_amt) * 2
    winnings = bank_amt + bet_double

    with open('mainbank.json', 'r') as f:
        data = json.load(f)
    data[str(user.id)]["bank"] = winnings
    with open('mainbank.json', 'w') as y:
        json.dump(data, y, indent=4)
    return True

async def bet_lose(user, bet_amt):
    users = await get_bank_data()
    bank_amt = users[str(user.id)]["bank"]
    winnings = bank_amt - int(bet_amt)

    with open('mainbank.json', 'r') as f:
        data = json.load(f)
    data[str(user.id)]["bank"] = winnings
    with open('mainbank.json', 'w') as y:
        json.dump(data, y, indent=4)
    return True

async def get_stock_json():
    with open("stocks.json", "r") as f:
        stocks = json.load(f)
    return stocks

async def get_price(symbol):
    stocks = await get_stock_json()
    stock_link = stocks[symbol]["link"]

    response = requests.get(stock_link)
    soup = BeautifulSoup(response.text, 'lxml')
    price = soup.find_all('div', {'class': 'My(6px) Pos(r) smartphone_Mt(6px)'})[0].find('span').text
    #print(price)
    return price

async def get_name(symbol):
    stocks = await get_stock_json()
    stock_name = stocks[symbol]["name"]
    return stock_name

async def get_logo(symbol):
    stocks = await get_stock_json()
    stock_logo = stocks[symbol]["logo"]
    return stock_logo
### Helper Functions

### Music Commands ###
@client.command(name='leave', help='Allows bot to leave the voice channel')
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    await voice_client.disconnect()

@client.command(name='play', help='Use this to play a song')
async def play(ctx):
    global music_queue

    if not ctx.message.author.voice:
        await ctx.send('You are not connected to a voice channel')
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()

    server = ctx.message.guild
    voice_channel = server.voice_client

    async with ctx.typing():
        player = await YTDLSource.from_url(music_queue[0], loop=client.loop)
        voice_channel.play(player, after=lambda e: print('Player Error: %s' %e) if e else None)
        del(music_queue[0])

    await ctx.send(f'**Now playing:** {player.title}')

@client.command(name='pause', help='Pause the current song playing')
async def pause(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.pause()

@client.command(name='resume', help='Resume the current paused song')
async def resume(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.resume()

@client.command(name='stop', help='Stops the current song playing')
async def stop(ctx):
    server = ctx.message.guild
    voice_channel = server.voice_client

    voice_channel.stop()

@client.command(name='queue', help='Add a song to the queue')
async def queue(ctx, url):
    global music_queue

    music_queue.append(url)
    await ctx.send(f'`{url}` has been added to the queue')

@client.command(name='viewqueue', help="View's the current queue")
async def viewqueue(ctx):
    await ctx.send(f'The current queue is: `{music_queue}`')

@client.command(name='remove', help='Removes song index from the queue')
async def remove(ctx, number):
    global music_queue

    try:
        del(music_queue[int(number)])
        await ctx.send(f'Your queue is now `{music_queue}`')
    except:
        await ctx.send('Your queue is either **empty** or the index is **out of range**')
## Music Commands ##

## Economy Commands ##
shop_role = 25000
shop_voice_channel = 10000

@client.command(name="shop", help="View the shop list")
async def shop(ctx):
    user = ctx.author
    server = ctx.guild.name

    em = discord.Embed(title=f"{server}'s Shop", color=discord.Color.blue())
    em.add_field(name="High Roller", value=f"${shop_role}\n*.buy pass*", )
    em.add_field(name="Personal Voice Channel", value=f"${shop_voice_channel}\n*.buy voicechannel*")
    await ctx.send(embed=em)


@client.command(name="buy", help="Used to buy an item from .shop")
async def buy(ctx, item):
    users = await get_bank_data()
    user = ctx.author
    bank_amt = users[str(user.id)]["bank"]
    role_cost = 25000
    voice_channel_cost = 10000

    if item == "pass" and bank_amt >= role_cost:
        new_balance = bank_amt - role_cost
        role = discord.utils.get(ctx.guild.roles, name="High Roller")
        if role in ctx.author.roles:
            pass_refund = bank_amt + role_cost
            # Updates user balance
            with open('mainbank.json', 'r') as f:
                data = json.load(f)
            data[str(user.id)]["bank"] = pass_refund
            with open('mainbank.json', 'w') as y:
                json.dump(data, y, indent=4)
            await ctx.author.remove_roles(role)
            await ctx.send(f"Your previous purchase of the role: **{role}** has been refunded. Your new balance is **${pass_refund}**")
        else:
            await discord.Member.add_roles(user, role)
            # Updates user balance
            with open('mainbank.json', 'r') as f:
                data = json.load(f)
            data[str(user.id)]["bank"] = new_balance
            with open('mainbank.json', 'w') as y:
                json.dump(data, y, indent=4)
            await ctx.send(f'You have successfully bought the **{role}**. Your new balance is ${new_balance}')
    elif item == "voicechannel" and bank_amt >= voice_channel_cost:
        guild = ctx.message.guild
        channel_name = f"{user.name}'s Office"
        existing_channel = discord.utils.get(guild.channels, name=channel_name)
        balance = bank_amt - voice_channel_cost
        if existing_channel == None:
            # Updates user balance
            with open('mainbank.json', 'r') as f:
                data = json.load(f)
            data[str(user.id)]["bank"] = balance
            with open('mainbank.json', 'w') as y:
                json.dump(data, y, indent=4)
            await guild.create_voice_channel(channel_name)
            await ctx.send(f"You are now the proud owner of **{user.name}'s Office**. Your new balance is **${balance}**")
        else:
            if existing_channel is not None:
                newer_balance = bank_amt + voice_channel_cost
                # Updates user balance
                with open('mainbank.json', 'r') as f:
                    data = json.load(f)
                data[str(user.id)]["bank"] = newer_balance
                with open('mainbank.json', 'w') as y:
                    json.dump(data, y, indent=4)
                await existing_channel.delete()
                await ctx.send(f"Your previous channel named **{user.name}'s Office** has been deleted. You have been refunded **${voice_channel_cost}**. Your new balance is **${newer_balance}**")
                # else:
                # await ctx.send(f'No channel named, "{channel_name}", was found.')
    else:
        await ctx.send("You do not have enough money for this purchase")
## Economy Commands ##

## Stock Commands ##
@client.command(name='price', help='Displays the current market price: .price (market symbol)')
async def price(ctx, symbol):
    price = await get_price(symbol)
    stock_name = await get_name(symbol)
    stock_logo = await get_logo(symbol)

    em = discord.Embed(title=f"{symbol}", description=f"{stock_name}", color=discord.Color.green())
    em.add_field(name="Current Market Price", value=f"${price}")
    em.set_thumbnail(url=stock_logo)
    await ctx.send(embed=em)
    #await ctx.send(f'{symbol} ({stock_name}): **${price}**')

@client.command(name="stocklist", help="Displays current market symbols compatible with .price")
async def stocklist(ctx):
    stocks = await get_stock_json()
    stock_list = []
    for key in stocks:
        stock_list.append(key)

    em = discord.Embed(title="Stock List", description="Stocks currently compatible to look up", color=discord.Color.dark_magenta())
    em.add_field(name=stock_list, value="symbols")
    await ctx.send(embed=em)
## Stock Commands

### Tasks ###


### Run Bot w/ Token ###
client.run(token)
