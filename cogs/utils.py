import asyncio
import config
import typing
import discord
import re
import time
from urllib.parse import quote_plus
from utils.buttons import SpotifyButton, ButtonDelete
from utils.cmds import get_graph, Spotify, UTC
from io import BytesIO
from datetime import datetime
from discord.ext import commands
from discord.utils import _URL_REGEX
from typing import Union


class MyUtils(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.utc = UTC()

    def get_new_embed(self, new_emote: discord.Emoji, ctx: commands.Context) -> discord.Embed:
        em = discord.Embed(title="Emoji Added",
                           description=f"**Emoji** - {new_emote}"
                                       f"\n**Emoji name** - {new_emote.name}"
                                       f"\n**Emoji ID** - {new_emote.id}"
                                       f"\n**URL** - [Emoji Url]({new_emote.url})"
                                       f"\n**Added by** - {ctx.author.mention}",
                           color=self.client.theme)
        return em

    @commands.command(aliases=['av', 'pfp'])
    async def avatar(self, ctx: commands.Context, member: typing.Union[discord.Member, discord.User] = None):
        """Displays a user's avatar"""
        member = member or ctx.author
        embed = discord.Embed(title='Showing avatar for {}'.format(member.name))
        embed.set_image(url=member.display_avatar.replace(size=1024).url)
        animated = ['png', 'jpg', 'jpeg', 'webp' if not member.display_avatar.is_animated() else 'gif']
        embed.description = " | ".join(
            [f"[{x.upper()}]({member.display_avatar.replace(format=x, size=1024).url})" for x in animated])
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(help="Checks the bot's ping to Discord")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def ping(self, ctx):
        pings = []
        number = 0

        typing_start = time.monotonic()
        await ctx.trigger_typing()
        typing_end = time.monotonic()
        typing_ms = (typing_end - typing_start) * 1000
        pings.append(typing_ms)

        start = time.perf_counter()
        message = await ctx.send("🏓 pong!")
        end = time.perf_counter()
        message_ms = (end - start) * 1000
        pings.append(message_ms)

        latency_ms = self.client.latency * 1000
        pings.append(latency_ms)

        for ms in pings:
            number += ms
        average = number / len(pings)

        await asyncio.sleep(0.7)

        await message.edit(content=re.sub('\n *', '\n',
                                          f"\n🌐 **| `Websocket ═╣ "
                                          f"{round(latency_ms, 3)}ms{' ' * (9 - len(str(round(latency_ms, 3))))}`** "
                                          f"\n<a:Loading:919929876566380635> **| `Typing ════╣ "
                                          f"{round(typing_ms, 3)}ms{' ' * (9 - len(str(round(typing_ms, 3))))}`**"
                                          f"\n:speech_balloon: **| `Message ═══╣ "
                                          f"{round(message_ms, 3)}ms{' ' * (9 - len(str(round(message_ms, 3))))}`**"
                                          f"\n:infinity: **| `Average ═══╣ "
                                          f"{round(average, 3)}ms{' ' * (9 - len(str(round(average, 3))))}`**"))

    @commands.command(aliases=['nsfwcheck', 'check'])
    async def nsfw_check(self, ctx: commands.Context, url: typing.Union[discord.Member, discord.User, str] = None):
        url = url or ctx.author
        base_url = "https://api.openrobot.xyz/api/nsfw-check"
        if isinstance(url, (discord.Member, discord.User)):
            session = await self.client.session.get(base_url, headers={"Authorization": config.OPEN_API},
                                                    params={"url": url.avatar.url})
            response: dict = await session.json()
        else:
            regex = _URL_REGEX
            found = re.search(regex, url)
            if found:
                url = found[0].replace('<', '').replace('>', '')
                print(url)
                session = await self.client.session.get(base_url, headers={"Authorization": config.OPEN_API},
                                                        params={"url": url})
                response: dict = await session.json()
            else:
                return await ctx.reply("Invalid argument detected")
        avatar: str = response.get('image_url')
        if not avatar:
            avatar: str = url.avatar.url if isinstance(url, (discord.Member, discord.User)) else url
        nsfw_score: int = round(response['nsfw_score'] * 100, 3)
        remainder = round(100 - nsfw_score, 3)
        embed = discord.Embed(title="NSFW Score", color=self.client.theme, timestamp=datetime.utcnow())
        embed.add_field(name="<:dnd:915110652958363668> Not Safe", value=f"**`{nsfw_score}`**")
        embed.add_field(name="<:online:907296805040062465> Safe", value=f"**`{remainder}`**")
        embed.set_footer(icon_url=ctx.author.avatar.url, text=f"Requested By: {ctx.author.name}")
        embed.set_image(url=avatar)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(brief="Steal an emote from a server with its id")
    @commands.has_permissions(manage_emojis=True)
    async def steal(self, ctx, emote: Union[discord.Emoji, str] = None):
        if emote is None and ctx.message.reference is None:
            return await ctx.send("Please provide a valid discord emoji or reply to a text with an emoji!")
        if ctx.message.reference is not None and emote is None:
            ww = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            txt = ww.content
            pt = "<(?P<animated>a?):(?P<name>[a-zA-Z0-9_]{2,32}):(?P<id>[0-9]{18,22})>"
            ss = re.search(pt, txt)
            try:
                ss = ss.group()
                ss = ss.replace('<', '').replace('>', '').split(':')
            except AttributeError:
                return await ctx.send("No emoji's were found within the text you referenced!")
            try:
                if ss[0] == 'a':

                    name = ss[1]
                    id = ss[2]
                    async with self.client.session.get(f"https://cdn.discordapp.com/emojis/{id}.gif") as r:
                        if r.status != 200:
                            print(r.status)
                            return await ctx.send(
                                "A random error occured, please contact bot owner for more information!")
                        data = BytesIO(await r.read())
                    new_emote = await ctx.guild.create_custom_emoji(name=name, image=data.getvalue())
                    em = self.get_new_embed(new_emote, ctx)
                    em.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{id}.gif")
                    return await ctx.send(embed=em)
                else:
                    name = ss[1]
                    id = ss[2]
                    async with self.client.session.get(f"https://cdn.discordapp.com/emojis/{id}.png") as r:
                        if r.status != 200:
                            print(r.status)
                            return await ctx.send(
                                "A random error occured, please contact bot owner for more information!")
                        data = BytesIO(await r.read())
                    new_emote = await ctx.guild.create_custom_emoji(name=name, image=data.getvalue())
                    em = self.get_new_embed(new_emote, ctx)
                    em.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{id}.png")
                    return await ctx.send(embed=em)
            except IndexError:
                return await ctx.send("No emoji's were found within the text you referenced!")
        try:
            if emote.animated is False:
                async with self.client.session.get(f"https://cdn.discordapp.com/emojis/{emote.id}.png") as resp:
                    if resp.status != 200:
                        return await ctx.send(
                            "A random error occured, please contact bot owner for more information!")
                    data = BytesIO(await resp.read())
                new_emote = await ctx.guild.create_custom_emoji(name=emote.name, image=data.getvalue())
                em = self.get_new_embed(new_emote, ctx)
                em.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emote.id}.png")
                return await ctx.send(embed=em)
            if emote.animated is True:
                async with self.client.session.get(f"https://cdn.discordapp.com/emojis/{emote.id}.gif") as resp:
                    if resp.status != 200:
                        print(resp.status)
                        return await ctx.send(
                            "A random error occured, please contact bot owner for more information!")
                    data = BytesIO(await resp.read())
                new_emote = await ctx.guild.create_custom_emoji(name=emote.name, image=data.getvalue())
                em = self.get_new_embed(new_emote, ctx)
                em.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{emote.id}.gif")
                return await ctx.send(embed=em)

        except AttributeError:
            x = str(emote)
            x = x.replace('<', '').replace('>', '').split(':')
            try:
                if x[0] == 'a':

                    name = x[1]
                    id = x[2]
                    async with self.client.session.get(f"https://cdn.discordapp.com/emojis/{id}.gif") as r:
                        if r.status != 200:
                            return await ctx.send(
                                "Please provide a valid discord emoji or reply to a text with an emoji!")
                        data = BytesIO(await r.read())
                    new_emote = await ctx.guild.create_custom_emoji(name=name, image=data.getvalue())
                    em = self.get_new_embed(new_emote, ctx)
                    em.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{id}.gif")
                    return await ctx.send(embed=em)
                else:

                    name = x[1]
                    id = x[2]
                    async with self.client.session.get(f"https://cdn.discordapp.com/emojis/{id}.png") as r:
                        if r.status != 200:
                            return await ctx.send(
                                "Please provide a valid discord emoji or reply to a text with an emoji!")
                        data = BytesIO(await r.read())
                    new_emote = await ctx.guild.create_custom_emoji(name=name, image=data.getvalue())
                    em = self.get_new_embed(new_emote, ctx)
                    em.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{id}.png")
                    return await ctx.send(embed=em)
            except IndexError:
                try:
                    x = x[0]
                    if str(x).startswith("$(a)"):
                        try:
                            x = int(str(x).replace('$(a)', ''))
                        except ValueError:
                            return await ctx.send(f"Please use `{ctx.prefix}info steal` for more info on the command!")
                        async with self.client.session.get(f"https://cdn.discordapp.com/emojis/{x}.gif") as r:
                            if r.status != 200:
                                return await ctx.send(
                                    "Please provide a valid discord emoji or reply to a text with an emoji!")
                            data = BytesIO(await r.read())
                        name = "DefaultX"
                        new_emote = await ctx.guild.create_custom_emoji(name=name, image=data.getvalue())
                        em = self.get_new_embed(new_emote, ctx)
                        em.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{x}.gif")
                        return await ctx.send(embed=em)
                    x = int(x)

                    async with self.client.session.get(f"https://cdn.discordapp.com/emojis/{x}.png") as r:
                        if r.status != 200:
                            return await ctx.send(
                                "Please provide a valid discord emoji or reply to a text with an emoji!")
                        data = BytesIO(await r.read())

                    name = "DefaultX"
                    new_emote = await ctx.guild.create_custom_emoji(name=name, image=data.getvalue())
                    em = self.get_new_embed(new_emote, ctx)
                    em.set_thumbnail(url=f"https://cdn.discordapp.com/emojis/{x}.png")
                    return await ctx.send(embed=em)
                except ValueError:
                    return await ctx.send("Please provide a valid discord emoji or reply to a text with an emoji!")

    @commands.command()
    async def graph(self, ctx: commands.Context, *points):
        points = [x for x in points if x.isdigit()]
        match points:
            case points if len(points) > 250:
                return await ctx.reply('You can\'t input more than 250 points')
            case points if len(points) < 4:
                return await ctx.reply('You are supposed to mention at least 4 points to plot a graph!',
                                       mention_author=False)
        filen = await get_graph(self.client, *points)
        view = ButtonDelete(ctx)
        await ctx.send(file=filen, view=view)

    @commands.command(aliases=['sp'])
    @commands.cooldown(5, 60.0, type=commands.BucketType.user)
    async def spotify(self, ctx: commands.Context, member: discord.Member = None):
        if not ctx.interaction and not member:
            member = (await ctx.guild.query_members(user_ids=[ctx.author.id]))[0]
        else:
            member = member or ctx.author
        async with ctx.typing():
            spotify = Spotify(bot=self.client, member=member)
            embed = await spotify.get_embed()
            if not embed:
                if member == ctx.author:
                    return await ctx.send(f"You are currently not listening to spotify!", mention_author=False)
                return await ctx.reply(f"{member.mention} is not listening to Spotify", mention_author=False,
                                       allowed_mentions=discord.AllowedMentions(users=False))
            activity = discord.utils.find(lambda act: isinstance(act, discord.Spotify), member.activities)
            view = SpotifyButton(ctx, activity)
            view.message = await ctx.send(embed=embed[0], file=embed[1], view=view)


def setup(client):
    client.add_cog(MyUtils(client))
