import config
import discord
from utils import cmds
from VishAPI.client import *
from discord.ext import commands
from typing import Union, Optional


class Fun(commands.Cog):
    def __init__(self, bot) -> None:
        self.genshin = None
        self.image = None
        self.bot = bot
        self.bot.loop.create_task(self.set_class_vars())

    async def set_class_vars(self):
        await self.bot.wait_until_ready()
        self.image = ImageEndpoint(api_key=config.VISHAPI, session=self.bot.session, io=True)
        self.genshin = GenshinEndpoint(api_key=config.VISHAPI, session=self.bot.session)

    @commands.command(aliases=['solar'])
    async def solarize(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        image = await self.image.request(ctx.command.name, url=avatar)
        embed = discord.Embed(title=f'Solarized image of {member.display_name}')
        embed.set_image(url=f"attachment://{ctx.command.name}.png")
        file = discord.File(fp=image, filename=f"{ctx.command.name}.png")
        await ctx.reply(embed=embed, file=file, mention_author=False)

    @commands.command()
    async def invert(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        image = await self.image.request(ctx.command.name, url=avatar)
        embed = discord.Embed(title=f'Inverted image of {member.display_name}')
        embed.set_image(url=f"attachment://{ctx.command.name}.png")
        file = discord.File(fp=image, filename=f"{ctx.command.name}.png")
        await ctx.reply(embed=embed, file=file, mention_author=False)

    @commands.command()
    async def blur(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        image = await self.image.request(ctx.command.name, url=avatar)
        embed = discord.Embed(title=f'Blurred image of {member.display_name}')
        embed.set_image(url=f"attachment://{ctx.command.name}.png")
        file = discord.File(fp=image, filename=f"{ctx.command.name}.png")
        await ctx.reply(embed=embed, file=file, mention_author=False)

    @commands.command(aliases=['embo'])
    async def emboss(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        image = await self.image.request(ctx.command.name, url=avatar)
        embed = discord.Embed(title=f'Embossed image of {member.display_name}')
        embed.set_image(url=f"attachment://{ctx.command.name}.png")
        file = discord.File(fp=image, filename=f"{ctx.command.name}.png")
        await ctx.reply(embed=embed, file=file, mention_author=False)

    @commands.command(aliases=['fg'])
    async def frostedglass(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        image = await self.image.request(ctx.command.name, url=avatar)
        embed = discord.Embed(title=f'Frosted Glassed image of {member.display_name}')
        embed.set_image(url=f"attachment://{ctx.command.name}.png")
        file = discord.File(fp=image, filename=f"{ctx.command.name}.png")
        await ctx.reply(embed=embed, file=file, mention_author=False)

    @commands.command()
    async def mirror(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        image = await self.image.request(ctx.command.name, url=avatar)
        embed = discord.Embed(title=f'Mirrored image of {member.display_name}')
        embed.set_image(url=f"attachment://{ctx.command.name}.png")
        file = discord.File(fp=image, filename=f"{ctx.command.name}.png")
        await ctx.reply(embed=embed, file=file, mention_author=False)

    @commands.command()
    async def lego(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        image = await self.image.request(ctx.command.name, url=avatar)
        embed = discord.Embed(title=f'Lego-ed image of {member.display_name}')
        embed.set_image(url=f"attachment://{ctx.command.name}.png")
        file = discord.File(fp=image, filename=f"{ctx.command.name}.png")
        await ctx.reply(embed=embed, file=file, mention_author=False)

    @commands.command()
    async def oil(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        image = await self.image.request(ctx.command.name, url=avatar)
        embed = discord.Embed(title=f'Oil Painted image of {member.display_name}')
        embed.set_image(url=f"attachment://{ctx.command.name}.png")
        file = discord.File(fp=image, filename=f"{ctx.command.name}.png")
        await ctx.reply(embed=embed, file=file, mention_author=False)

    @commands.command()
    async def flip(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        image = await self.image.request(ctx.command.name, url=avatar)
        embed = discord.Embed(title=f'Flipped image of {member.display_name}')
        embed.set_image(url=f"attachment://{ctx.command.name}.png")
        file = discord.File(fp=image, filename=f"{ctx.command.name}.png")
        await ctx.reply(embed=embed, file=file, mention_author=False)

    @commands.command(aliases=['ht'])
    async def halftone(self, ctx: commands.Context, member: Union[discord.Member, discord.User] = None):
        member = member or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        image = await self.image.request(ctx.command.name, url=avatar)
        embed = discord.Embed(title=f'Halftoned image of {member.display_name}')
        embed.set_image(url=f"attachment://{ctx.command.name}.png")
        file = discord.File(fp=image, filename=f"{ctx.command.name}.png")
        await ctx.reply(embed=embed, file=file, mention_author=False)

    @commands.command(aliases=['gradient', 'grad'])
    async def filter(self, ctx: commands.Context, member: Optional[Union[discord.Member, discord.User]] = None,
                     gradient: str = "oceanic"):
        possible = "dramatic, firenze, golden, lix, lofi, neue, obsidian, pastel_pink, ryo, oceanic, marine, " \
                   "seagreen, flagblue, liquid, diamante , radio, twenties, rosetint, mauve, bluechrome, vintage, " \
                   "perfume, serenity"
        new_possibles = [text.strip() for text in possible.split(', ')]
        if gradient == "list":
            actual = ', '.join([f"`{text}`" for text in new_possibles])
            return await ctx.reply(f"Here are all the possible gradients: {actual}\n**Default:** `oceanic`")
        if gradient not in new_possibles:
            return await ctx.send(
                f"An Inappropriate Gradient was passed, use `{ctx.prefix}gradient list` to check all gradients possible")
        member = member if isinstance(member, (discord.Member, discord.User)) else ctx.author or ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        image = await self.image.request(ctx.command.name, url=avatar, filter=gradient)
        embed = discord.Embed(title=f'Image of {member.display_name} with {gradient} Filter')
        embed.set_footer(text=f"User {ctx.prefix}filter list to get a list of all the filters")
        embed.set_image(url=f"attachment://{ctx.command.name}.png")
        file = discord.File(fp=image, filename=f"{ctx.command.name}.png")
        await ctx.reply(embed=embed, file=file, mention_author=False)

    @commands.command()
    async def round(self, ctx: commands.Context):
        member = ctx.author
        avatar = member.avatar.url if member.avatar else member.default_avatar.url
        session = await bot.session.get(avatar)
        byte = BytesIO(await session.read())
        image = cmds.get_pictute(byte)
        file = discord.File(fp=image, filename="rounded.png")
        await ctx.send(file=file)


def setup(bot):
    bot.add_cog(Fun(bot))
