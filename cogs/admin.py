import discord
from discord.ext import commands, tasks
from discord.utils import get
import asyncio
import youtube_dl
from random import choice
import os, json, random
import main

class Admin(commands.Cog):
    def __init__(self, client):
        self.client = client


def setup(client):
    client.add_cog(Admin(client))