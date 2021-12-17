import discord
from discord.ext import commands


class HelpClass(commands.HelpCommand):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


class HelpCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(HelpCog(bot))
