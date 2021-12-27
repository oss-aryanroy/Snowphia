from discord.ext import commands


class HelpClass(commands.HelpCommand):
    def __init__(self, **kwargs):
        """
        Subclass of commands.HelpCommand for Bot help command
        """
        super().__init__(**kwargs)


class HelpCog(commands.Cog):
    def __init__(self, bot):
        """
        Cog Subclass for registering HelpClass
        """
        self.bot = bot


def setup(bot):
    bot.add_cog(HelpCog(bot))
