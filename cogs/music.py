"""
This example cog demonstrates basic usage of Lavalink.py, using the DefaultPlayer.
As this example primarily showcases usage in conjunction with discord.py, you will need to make
modifications as necessary for use with another Discord library.
Usage of this cog requires Python 3.6 or higher due to the use of f-strings.
Compatibility with Python 3.5 should be possible if f-strings are removed.
"""
import re

import discord
import lavalink
from discord.ext import commands

url_rx = re.compile(r'https?://(?:www\.)?.+')


class LavalinkVoiceClient(discord.VoiceClient):
    def __init__(self, client: commands.AutoShardedBot, channel: discord.abc.Connectable):
        self.client = client
        self.channel = channel
        # ensure there exists a client already
        if hasattr(self.client, 'lavalink'):
            self.lavalink = self.client.lavalink
        else:
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node(
                'localhost',
                2333,
                'youshallnotpass',
                'us',
                'default-node')
            self.lavalink = self.client.lavalink

    async def on_voice_server_update(self, data):
        lavalink_data = {
            't': 'VOICE_SERVER_UPDATE',
            'd': data
        }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def on_voice_state_update(self, data):
        lavalink_data = {
            't': 'VOICE_STATE_UPDATE',
            'd': data
        }
        await self.lavalink.voice_update_handler(lavalink_data)

    async def connect(self, *, timeout: float, reconnect: bool) -> None:
        self.lavalink.player_manager.create(guild_id=self.channel.guild.id)
        await self.channel.guild.change_voice_state(channel=self.channel)

    async def disconnect(self, *, force: bool) -> None:
        player = self.lavalink.player_manager.get(self.channel.guild.id)
        if not force and not player.is_connected:
            return
        await self.channel.guild.change_voice_state(channel=None)
        player.channel_id = None
        self.cleanup()


class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def convert(*args):
        standard = (1, 60, 3600, 21600)[:len(args)]
        return sum([args[standard.index(stand)] * stand for stand in standard])

    @staticmethod
    async def handle_except(player: lavalink.DefaultPlayer, ctx: commands.Context):
        if not player.is_connected:
            return await ctx.send('Bot is not connected to a VC')
        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send('You\'re not in my Voice Channel!')

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        if not hasattr(self.bot, 'lavalink'):  # This ensures the client isn't overwritten during cog reloads.
            self.bot.lavalink = lavalink.Client(self.bot.user.id)
            self.bot.lavalink.add_node('localhost', 2333, 'youshallnotpass', 'us',
                                       'default-node')  # Host, Port, Password, Region, Name

        lavalink.add_event_hook(self.track_hook)

    def cog_unload(self):
        self.bot.lavalink._event_hooks.clear()

    async def cog_before_invoke(self, ctx):
        guild_check = ctx.guild is not None
        if guild_check:
            await self.ensure_voice(ctx)

        return guild_check

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send(error.original)

    async def get_correct_thumbnail(self, track: lavalink.AudioTrack):
        priority = ('maxresdefault', 'hq720', 'sddefault')
        for value in priority:
            url = f"https://i.ytimg.com/vi/{track.identifier}/{value}.jpg"
            session = await self.bot.session.get(url)
            if session.ok:
                return url
            continue
        return False

    async def ensure_voice(self, ctx):
        player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        should_connect = ctx.command.name in ('play',)

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise commands.CommandInvokeError('Join a voicechannel first.')
        if not player.is_connected:
            if not should_connect:
                raise commands.CommandInvokeError('Not connected.')
            permissions = ctx.author.voice.channel.permissions_for(ctx.me)
            if not permissions.connect or not permissions.speak:
                raise commands.CommandInvokeError('I need the `CONNECT` and `SPEAK` permissions.')
            player.store('channel', ctx.channel.id)
            await ctx.author.voice.channel.connect(cls=LavalinkVoiceClient)
        else:
            if int(player.channel_id) != ctx.author.voice.channel.id:
                raise commands.CommandInvokeError('You need to be in my voicechannel.')

    async def track_hook(self, event):
        if isinstance(event, lavalink.events.QueueEndEvent):
            guild_id = int(event.player.guild_id)
            guild = self.bot.get_guild(guild_id)
            await guild.voice_client.disconnect(force=True)

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, query: str):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        query = query.strip('<>')
        if not url_rx.match(query):
            query = f'ytsearch:{query}'
        results = await player.node.get_tracks(query)
        if not results or not results['tracks']:
            return await ctx.send('Nothing found!')
        embed = discord.Embed(color=self.bot.theme)
        if results['loadType'] == 'PLAYLIST_LOADED':
            tracks = results['tracks']
            await ctx.send(tracks[0])
            url = await self.get_correct_thumbnail(tracks[0])
            if not url:
                url = "https://www.example.jpg"
            for track in tracks:
                player.add(requester=ctx.author.id, track=track)
            embed.title = 'Playlist Enqueued!'
            embed.set_image(url=url)
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
        else:
            track = results['tracks'][0]
            embed.title = 'Track Has been added to queue'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'

            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True)
            url = await self.get_correct_thumbnail(track)
            if not url:
                url = "https://www.example.jpg"
            embed.set_thumbnail(url=url)

            player.add(requester=ctx.author.id, track=track)
        await ctx.send(embed=embed)
        if not player.is_playing:
            await player.play()

    @commands.command()
    async def stop(self, ctx: commands.Context):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        await self.handle_except(player, ctx)
        player.queue.clear()
        await player.stop()

    @commands.command()
    async def skip(self, ctx: commands.Context):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        await self.handle_except(player, ctx)
        await player.skip()

    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        await self.handle_except(player, ctx)
        player.queue.clear()
        await player.stop()
        await ctx.voice_client.disconnect(force=True)
        await ctx.send('*⃣ | Disconnected.')


def setup(bot):
    bot.add_cog(Music(bot))
