import discord
from discord.ext import commands, tasks
from discord.utils import get
import asyncio
import youtube_dl
from random import choice
import os, json

noah_path = "C:\\Users\\noahw\\Desktop\\Coding\\Github Projects\\ThiccBot\\venv"
cody_path = ""

os.chdir(noah_path)

client = commands.Bot(command_prefix = '.')
token = 'NzU1NDQ5NjQ0NzIwMzI0NjQw.X2DdTg.ilG6fU6a_TU1jmlsmFbfX5N-fBg'

music_queue = []

### Music Setup ###
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

### Events ###
@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game("w/ Niggas"))
    print("Bot is online.")

@client.event
async def on_member_join(member):
    print(f'{member} has joined a server.')

@client.event
async def on_member_remove(member):
    print(f'{member} has left a server.')

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
#async def imposters(ctx, role: discord.Role = None):
    #await ctx.user.add_roles(member, role)

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

## Economy ##
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
        users[str(user.id)]["bank"] = 1000
        
    with open("mainbank.json", "w") as f:
        json.dump(users, f)
    return True

@client.command(name= "balance", help="Checks your account balance")
async def balance(ctx):
    await open_account(ctx.author)

    user = ctx.author
    users = await get_bank_data()

    bank_amt = users[str(user.id)]["bank"]

    em = discord.Embed(title=f"{ctx.author.name}'s Bank Account", color= discord.Color.red())
    em.add_field(name= "Balance", value= f'${bank_amt}')
    await ctx.send(embed= em)

### Tasks ###


### Run Bot w/ Token ###
client.run(token)