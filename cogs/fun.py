import discord
from discord.ext import commands
from utils.cmds import VishAPI
from typing import Union, Optional

class Fun(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(aliases=['solar'])
    async def solarize(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        vish = VishAPI(self.bot, member)
        embed, file = await vish.get_embed(ctx.command.name, url=avatar)
        await ctx.reply(embed=embed, file=file,mention_author=False)

    @commands.command()
    async def invert(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        vish = VishAPI(self.bot, member)
        embed, file = await vish.get_embed(ctx.command.name, url=avatar)
        await ctx.reply(embed=embed, file=file,mention_author=False)

    @commands.command()
    async def blur(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        vish = VishAPI(self.bot, member)
        embed, file = await vish.get_embed(ctx.command.name, url=avatar)
        await ctx.reply(embed=embed, file=file,mention_author=False)

    @commands.command(aliases=['colors'])
    async def primary(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        vish = VishAPI(self.bot, member)
        embed, file = await vish.get_embed(ctx.command.name, url=avatar)
        await ctx.reply(embed=embed, file=file,mention_author=False)

    @commands.command(aliases=['embo'])
    async def emboss(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        vish = VishAPI(self.bot, member)
        embed, file = await vish.get_embed(ctx.command.name, url=avatar)
        await ctx.reply(embed=embed, file=file,mention_author=False)

    @commands.command(aliases=['fg'])
    async def frostedglass(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        vish = VishAPI(self.bot, member)
        embed, file = await vish.get_embed(ctx.command.name, url=avatar)
        await ctx.reply(embed=embed, file=file,mention_author=False)
        
    @commands.command()
    async def mirror(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        vish = VishAPI(self.bot, member)
        embed, file = await vish.get_embed(ctx.command.name, url=avatar)
        await ctx.reply(embed=embed, file=file,mention_author=False)

    @commands.command()
    async def lego(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        vish = VishAPI(self.bot, member)
        embed, file = await vish.get_embed(ctx.command.name, url=avatar)
        await ctx.reply(embed=embed, file=file,mention_author=False)

    @commands.command()
    async def oil(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        vish = VishAPI(self.bot, member)
        embed, file = await vish.get_embed(ctx.command.name, url=avatar)
        await ctx.reply(embed=embed, file=file,mention_author=False)
    
    @commands.command()
    async def flip(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        vish = VishAPI(self.bot, member)
        embed, file = await vish.get_embed(ctx.command.name, url=avatar)
        await ctx.reply(embed=embed, file=file ,mention_author=False)

    @commands.command(aliases=['ht'])
    async def halftone(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        vish = VishAPI(self.bot, member)
        embed, file = await vish.get_embed(ctx.command.name, url=avatar)
        await ctx.reply(embed=embed, file=file ,mention_author=False)

    @commands.command(aliases=['gradient', 'grad'])
    async def filter(self, ctx: commands.Context, member: Optional[Union[discord.Member, discord.User]] = None, gradient: str = "oceanic"):
        possible = "dramatic, firenze, golden, lix, lofi, neue, obsidian, pastel_pink, ryo, oceanic, marine, seagreen, flagblue, liquid, diamante , radio, twenties, rosetint, mauve, bluechrome, vintage, perfume, serenity"
        new_possibles = possible.split(', ')
        if gradient == "list":
            actual = ', '.join([f"`{text}`" for text in possible.split(', ')])
            return await ctx.reply(f"Here are all the possible gradients: {actual}\n**Default:** `oceanic`")
        if gradient not in new_possibles:
                return await ctx.send(f"An Inappropriate Gradient was passed, use `{ctx.prefix}gradient list` to check all gradients possible")
        member = member if isinstance(member, (discord.Member, discord.User)) else ctx.author or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        vish = VishAPI(self.bot, member)
        embed, file = await vish.get_embed(ctx.command.name, url=avatar, filter=gradient.lower())
        await ctx.reply(embed=embed, file=file ,mention_author=False)

def setup(bot):
    bot.add_cog(Fun(bot))
