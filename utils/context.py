from discord.ext import commands
from h11 import Data
from db import Database

class CustomContext(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.db = Database(self.bot)