import config
import discord
from io import BytesIO
from utils import cmds
from VishAPI import NotFound
from VishAPI.objects import Character
from VishAPI.client import GenshinEndpoint, ImageEndpoint
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

    @commands.group()
    async def genshin(self, ctx: commands.Context):
        if not ctx.subcommand_passed:
            await ctx.send_help(ctx.command)

    @genshin.command(aliases=['char'])
    async def character(self, ctx: commands.Context, *, name: str):
        try:
            character: Character = await self.genshin.request('character', name.lower())
            embed = discord.Embed(title=f"About {character.name}", description="```css\n[General Description]"
                                                                               f"\n{character.description}\n\n"
                                                                               "[Game Description]"
                                                                               f"\n{character.game_description}\n```")
            act = "Actor" if "male" in character.gender else "Actress"
            iterable = [('Rating', character.star_rank),
                        ('Vision', character.vision),
                        ('Weapon', character.weapon),
                        ('Gender', character.gender),
                        ('Birthday', character.birthday),
                        ('Constellation', character.constellation),
                        (f'Japanese Voice {act}', character.voice_actor_jp),
                        ('\u200b', '\u200b'),
                        (f'English Voice {act}', character.voice_actor_en),
                        ]
            for name, value in iterable:
                embed.add_field(name=name, value=value)
            embed.set_image(url=character.image.url)
            await ctx.reply(embed=embed, mention_author=False)
        except NotFound:
            return await ctx.send(f'No character with the name \'{name}\' was found!')

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
        member = member or ctx.author
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
        session = await self.bot.session.get(avatar)
        byte = BytesIO(await session.read())
        image = await cmds.get_picture(byte)
        file = discord.File(fp=image, filename="rounded.png")
        await ctx.send(file=file)


def setup(bot):
    bot.add_cog(Fun(bot))
