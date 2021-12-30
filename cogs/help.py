import discord
import datetime
from discord.ext import commands


class HelpClass(commands.HelpCommand):
    def __init__(self, **kwargs):
        """
        Subclass of commands.HelpCommand for Bot help command
        """
        super().__init__(**kwargs)
        self.important = "```yaml\n(c) means command | (g) means group \n([]) is required  | (<>) is optional\n```"

    def generate_params(self, command: commands.Command):
        parameters = command.clean_params
        some_string = ", ".join([(f"`<{name}>`" if parameter.default is parameter.empty else f"`[{name}]`") for name, parameter in parameters.items()])
        if not some_string:
            some_string = "`None`"
        return some_string

    async def send_command_help(self, command: commands.Command):
        cog = command.cog.qualified_name if command.cog else 'Miscellaneous'
        timestamp = datetime.datetime.utcnow()
        embed = discord.Embed(title=f"Help for {command.name}", 
                              color=self.context.bot.theme, 
                              timestamp=timestamp)
        embed.description = f"{self.important}\n`Command Category`: {cog}"
        documentation = command.help.replace("{prefix}", self.context.prefix) if command.help else "The command has yet to be documented"
        aliases = ", ".join([f"`{com}`" for com in command.aliases]) or '`None`'
        parameters = self.generate_params(command)
        to_add = [('Documentation', documentation), ('Aliases', aliases), ('Parameters', parameters)]
        for name, value in to_add:
            embed.add_field(name=name, value=value, inline=False)
        channel = self.get_destination()
        embed.set_footer(text=f"Request by: {self.context.author.name}")
        await channel.send(embed=embed)
    
    async def send_cog_help(self, cog: commands.Cog):
        string = ""
        cog_name = cog.qualified_name if cog else 'Miscellaneous'
        
        timestamp = datetime.datetime.utcnow()
        embed = discord.Embed(title=f"Help for {cog_name}", 
                              color=self.context.bot.theme, 
                              timestamp=timestamp)
        embed.description = f"{self.important}\n**Category**: {cog_name}\nType `{self.context.prefix}help [command]` to get more info on a command.\nType `{self.context.prefix}help [group]` to get more info on a group.\n"
        for command in cog.walk_commands():
            if isinstance(command, commands.Group):
                some_string = f"(g) {self.context.prefix}{command.qualified_name} "
                parameters = command.clean_params
                for name, parameter in parameters.items():
                    if parameter.default is parameter.empty:
                        some_string += f"[{name}] "
                    else:
                        some_string += f"<{name}> "
                string += some_string + "\n"
            elif isinstance(command, commands.Command):
                some_string = f"(c) {self.context.prefix}{command.qualified_name} "
                parameters = command.clean_params
                for name, parameter in parameters.items():
                    if parameter.default is parameter.empty:
                        some_string += f"[{name}] "
                    else:
                        some_string += f"<{name}> "
                string += some_string + "\n"
        new_split = [x.split() for x in string.split('\n')]
        new_order = sorted(new_split, key=len)
        new = map(' '.join, new_order)
        string = '\n'.join(new)
        embed.description += f"```css\n{string}\n```"
        channel = self.get_destination()
        embed.set_footer(text=f"Request by: {self.context.author.name}")
        await channel.send(embed=embed)
        

class HelpCog(commands.Cog):
    def __init__(self, bot):
        """
        Cog Subclass for registering HelpClass
        """
        self.bot = bot
        self.bot.help_command = HelpClass()
    
    

def setup(bot):
    bot.add_cog(HelpCog(bot))
