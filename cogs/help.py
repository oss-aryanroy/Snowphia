import discord
from discord.ext import commands


class HelpClass(commands.HelpCommand):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
