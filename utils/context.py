from discord.ext import commands
from db import Database

class CustomContext(commands.Context):
    __slots__ = ('db',)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database(self.bot)