import re
import asyncio
import discord
import config
from io import BytesIO
from datetime import datetime as dt
from datetime import timedelta, tzinfo
import random
import base64
import datetime
import string
import urllib
from typing import Tuple
from colorthief import ColorThief
import functools
from PIL import Image, ImageDraw, ImageFont
import numpy as np

ZERO = timedelta(0)


def executor(loop=None, execute=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            partial = functools.partial(func, *args, **kwargs)
            under_loop = loop or asyncio.get_event_loop()
            return under_loop.run_in_executor(execute, partial)

        return wrapper

    return decorator


class UTC(tzinfo):
    def utcoffset(self, dt) -> timedelta:
        return ZERO

    def tzname(self, dt) -> str:
        return "UTC"

    def dst(self, dt) -> timedelta:
        return ZERO


class VishAPI:
    __slots__ = ('api_key', 'bot', 'member')

    def __init__(self, bot, member) -> None:
        self.api_key = config.VISHAPI
        self.bot = bot
        self.member = member

    async def get_embed(self, endpoint: str, **kwargs) -> Tuple[discord.Embed, discord.File]:
        headers = {"Authorization": self.api_key}
        session = await self.bot.session.get(f"https://api.kozumikku.tech/image/{endpoint}", params=kwargs,
                                             headers=headers)
        print(session.status)
        file = discord.File(BytesIO(await session.read()), filename=f"{endpoint}.png")
        embed = discord.Embed(title=f"{endpoint.title()}-ed Image for {self.member.name}", color=self.bot.theme)
        embed.set_image(url=f"attachment://{endpoint}.png")
        return embed, file


class Spotify:
    __slots__ = ('member', 'bot', 'embed', 'regex', 'headers', 'counter')

    def __init__(self, *, bot, member) -> None:
        self.member = member
        self.bot = bot
        self.embed = discord.Embed(title=f"{member.display_name} is Listening to Spotify", color=self.bot.theme)
        self.regex = "(https\:\/\/open\.spotify\.com\/artist\/[a-zA-Z0-9]+)"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/75.0.3770.100 Safari/537.36'}
        self.counter = 0

    async def request_pass(self, *, track_id: str):
        try:
            if not self.bot.spotify_session or dt.utcnow() > self.bot.spotify_session[1]:
                resp = await self.bot.session.post("https://accounts.spotify.com/api/token",
                                                   params={"grant_type": "client_credentials"}, headers={
                        "Authorization": f'Basic {base64.urlsafe_b64encode(f"{self.bot.spotify_client_id}:{self.bot.spotify_client_secret}".encode()).decode()}',
                        "Content-Type": "application/x-www-form-urlencoded", }, )
                auth_js = await resp.json()
                timenow = dt.utcnow() + timedelta(seconds=auth_js['expires_in'])
                type_token = auth_js['token_type']
                token = auth_js['access_token']
                auth_token = f"{type_token} {token}"
                self.bot.spotify_session = (auth_token, timenow)
                print('Generated new Token')
            else:
                auth_token = self.bot.spotify_session[0]
                print('Using previous token')
        except Exception:
            return False
        else:
            try:
                resp = await self.bot.session.get(f"https://api.spotify.com/v1/tracks/{urllib.parse.quote(track_id)}",
                                                  params={
                                                      "market": "US",
                                                  },
                                                  headers={
                                                      "Authorization": auth_token},
                                                  )
                json = await resp.json()
                return json
            except Exception:
                if self.counter == 4:
                    return False
                else:
                    self.counter += 1
                    await self.request_pass(track_id=track_id)

    @staticmethod
    def pil_process(pic, name, artists, time, time_at, track):
        s = ColorThief(pic)
        color = s.get_palette(color_count=2)
        result = Image.new('RGBA', (575, 170))
        draw = ImageDraw.Draw(result)
        color_font = "white" if sum(color[0]) < 450 else "black"
        draw.rounded_rectangle(((0, 0), (575, 170)), 20, fill=color[0])
        s = Image.open(pic)
        s = s.resize((128, 128))
        result1 = Image.new('RGBA', (129, 128))
        Image.Image.paste(result, result1, (29, 23))
        Image.Image.paste(result, s, (27, 20))
        font = ImageFont.truetype(f"Assets/spotify.ttf", 28)
        font2 = ImageFont.truetype(f"Assets/spotify.ttf", 18)
        draw.text((170, 20), name, color_font, font=font)
        draw.text((170, 55), artists, color_font, font=font2)
        draw.text((500, 120), time, color_font, font=font2)
        draw.text((170, 120), time_at, color_font, font=font2)
        draw.rectangle(((230, 130), (490, 127)), fill="grey")  # play bar
        draw.rectangle(((230, 130), (230 + track, 127)), fill=color_font)
        draw.ellipse((230 + track - 5, 122, 230 + track + 5, 134), fill=color_font, outline=color_font)
        draw.ellipse((230 + track - 6, 122, 230 + track + 6, 134), fill=color_font, outline=color_font)
        output = BytesIO()
        result.save(output, "png")
        output.seek(0)
        return discord.File(fp=output, filename="spotify.png")

    async def get_from_local(self, bot, act: discord.Spotify) -> discord.File:
        s = tuple(f"{string.ascii_letters}{string.digits}{string.punctuation} ")
        artists = ', '.join(act.artists)
        artists = ''.join([x for x in artists if x in s])
        artists = artists[0:36] + "..." if len(artists) > 36 else artists
        time = act.duration.seconds
        time_at = (datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc) - act.start).total_seconds()
        track = (time_at / time) * 260
        time = f"{time // 60:02d}:{time % 60:02d}"
        time_at = f"{int((time_at if time_at > 0 else 0) // 60):02d}:{int((time_at if time_at > 0 else 0) % 60):02d}"
        pog = act.album_cover_url
        name = ''.join([x for x in act.title if x in s])
        name = name[0:21] + "..." if len(name) > 21 else name
        rad = await bot.session.get(pog)
        pic = BytesIO(await rad.read())
        return await bot.loop.run_in_executor(None, self.pil_process, pic, name, artists, time, time_at, track)

    @staticmethod
    async def fetch_from_api(bot, activity: discord.Spotify):
        act = activity
        base_url = "https://api.jeyy.xyz/discord/spotify"
        params = {'title': act.album, 'cover_url': act.album_cover_url, 'artists': act.artists[0],
                  'duration_seconds': act.duration.seconds, 'start_timestamp': int(act.start.timestamp())}
        connection = await bot.session.get(base_url, params=params)
        buffer = BytesIO(await connection.read())
        return discord.File(fp=buffer, filename="spotify.png")

    async def send_backup_artist_request(self, activity):
        artists = activity.artists
        url = activity.track_url
        result = await self.bot.session.get(url, headers=self.headers)
        text = await result.text()
        my_list = re.findall(self.regex, text)
        final = sorted(set(my_list), key=my_list.index)
        total = len(artists)
        final_total = final[0:total]
        final_string = ', '.join([f"[{artists[final_total.index(x)]}]({x})" for x in final_total])
        return final_string

    async def get_embed(self) -> Tuple[discord.Embed, discord.File]:
        activity = discord.utils.find(lambda activity: isinstance(activity, discord.Spotify), self.member.activities)
        if not activity:
            return False
        try:
            result = await self.request_pass(track_id=activity.track_id)
            final_string = ', '.join(
                [f"[{resp['name']}]({resp['external_urls']['spotify']})" for resp in result['artists']])
        except Exception:
            final_string = await self.send_backup_artist_request(activity)
        url = activity.track_url
        image = await self.get_from_local(self.bot, activity)
        self.embed.description = f"**Artists**: {final_string}\n**Album**: [{activity.album}]({url})"
        self.embed.set_image(url="attachment://spotify.png")
        return self.embed, image


async def humanize_alternative(ws) -> str or bool:
    returning = ""
    seconds = int(ws)
    if seconds <= 0:
        return False
    years, seconds = divmod(seconds, 31536000)
    months, seconds = divmod(seconds, 2628000)
    weeks, seconds = divmod(seconds, 604800)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    a_u_v = [years, months, weeks, days, hours, minutes, seconds]
    a_u_n = ["year", "month", "week", "day", "hour", "minute", "second"]
    op_list_v = []
    op_list_n = []
    for i in range(len(a_u_v)):
        if a_u_v[i] > 0:
            op_list_v.append(a_u_v[i])
            op_list_n.append(a_u_n[i])
    for i in range(len(op_list_v)):
        if i + 3 <= len(op_list_v):
            returning += f"{op_list_v[i]} {f'{op_list_n[i]}, ' if op_list_v[i] <= 1 else f'{op_list_n[i]}s, '}"
        elif i + 2 <= len(op_list_v):
            returning += f"{op_list_v[i]} {f'{op_list_n[i]} and ' if op_list_v[i] <= 1 else f'{op_list_n[i]}s and '}"
        else:
            returning += f"{op_list_v[i]} {op_list_n[i] if op_list_v[i] <= 1 else op_list_n[i] + 's'}"
    return returning


async def get_graph(bot, *args):
    og_dict = {
        "type": "line",
        "data": {
            "labels": [],
            "datasets": [
                {
                    "label": "Statistics",
                    "data": [],
                    "backgroundColor": "rgb(255, 99, 132)",
                    "borderColor": "rgb(255, 99, 132)",
                    "fill": 'false'
                }
            ]
        }
    }
    label1 = list(range(1, len(args) + 1))
    print(label1)
    data = [x for x in args]
    og_dict['data']['labels'] = label1
    og_dict['data']['datasets'][0]['data'] = data
    param = {"c": str(og_dict)}
    url = "https://quickchart.io/chart"
    s = await bot.session.get(url, params=param)
    ob = BytesIO(await s.read())
    return discord.File(fp=ob, filename="plot.png")


@executor()
def get_picture(image: BytesIO):
    img = Image.open(image)
    display(img)

    height, width = img.size
    lum_img = Image.new('L', (height, width), 0)

    draw = ImageDraw.Draw(lum_img)
    draw.pieslice(((0, 0), (height, width)), 0, 360,
                  fill=255, outline="white")
    img_arr = np.array(img)
    lum_img_arr = np.array(lum_img)
    display(Image.fromarray(lum_img_arr))
    final_img_arr = np.dstack((img_arr, lum_img_arr))
    image = Image.fromarray(final_img_arr)
    buffer = BytesIO()
    image.save(buffer, "PNG")
    buffer.seek(0)
    return buffer
