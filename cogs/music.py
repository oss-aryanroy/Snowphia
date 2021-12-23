import re
import discord
from discord.ext.commands.core import after_invoke
import lavalink
from typing import Union
from discord.ext import commands

url_rx = re.compile(r'https?://(?:www\.)?.+')


class LavalinkVoiceClient(discord.VoiceClient):
    def __init__(self, client: commands.AutoShardedBot, channel: discord.abc.Connectable):

        self.client = client
        self.channel = channel

        if hasattr(self.client, 'lavalink'):
            self.lavalink = self.client.lavalink
        else:
            self.client.lavalink = lavalink.Client(client.user.id)
            self.client.lavalink.add_node(
                                        'localhost',
                                        2333,
                                        'youshallnotpass',
                                        'us',
                                        'default-node'
                                        )  # Host, Port, Password, Region, Name
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

    @staticmethod
    def convert(*args):
        standard = (1, 60, 3600, 21600)[:len(args)]
        return sum([args[standard.index(stand)] * stand for stand in standard])

    @staticmethod
    async def handle_except(player: lavalink.PlayerManager, ctx: commands.Context):
        if not player.is_connected:
            return await ctx.send('Bot is not connected to a VC')
        if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
            return await ctx.send('You\'re not in my Voice Channel!')

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        if not hasattr(self.bot, 'lavalink'):
            self.bot.lavalink = lavalink.Client(self.bot.user.id)
            self.bot.lavalink.add_node('localhost', 
                                        2333, 
                                        'youshallnotpass', 
                                        'us',
                                        'default-node'
                                        )  # Host, Port, Password, Region, Name

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

    async def create_embed(self, guild: discord.Guild, track: lavalink.AudioTrack):
        channel_id = track.extra.get('channel_id')

        channel = guild.get_channel(channel_id)
        if channel is None:
            return

        requester = guild.get_member(track.requester)
        if requester is None:
            requester = "Unknown"
        else:
            requester = requester.display_name

        embed = discord.Embed(color=self.bot.theme)
        embed.title = 'Now playing:'
        embed.description = f'[{track.title}]({track.url})'
        embed.set_footer(text=f"Requested By: {requester}")
        await channel.send(embed=embed)

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
        elif isinstance(event, lavalink.events.TrackStartEvent):
            self.bot.dispatch('lavalink_track_start', event.player, event.track)

    
    @commands.Cog.listener()
    async def on_lavalink_track_start(self, player: lavalink.PlayerManager, track):
        guild = self.bot.get_guild(player.guild_id)
        await self.create_embed(guild, track)


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
            for track in tracks:
                track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True, channel_id=ctx.channel.id)
                player.add(requester=ctx.author.id, track=track, channel_id=ctx.channel.id)
            embed.title = 'Tracks Have been added to the queue'
            embed.description = f'{results["playlistInfo"]["name"]} - {len(tracks)} tracks'
        else:
            track = results['tracks'][0]
            embed.title = 'Track Has been added to queue'
            embed.description = f'[{track["info"]["title"]}]({track["info"]["uri"]})'
            track = lavalink.models.AudioTrack(track, ctx.author.id, recommended=True, channel_id=ctx.channel.id)
            player.add(requester=ctx.author.id, track=track)
        await ctx.send(embed=embed)
        await ctx.message.add_reaction('<a:PurpleCheck:922496654739902474>')
        if not player.is_playing:
            await player.play()

    @commands.command()
    async def seek(self, ctx: commands.Context, *, timestamp: Union[int, str]):
        if isinstance(timestamp, str):
            try:
                time = self.convert(*[int(s) for s in timestamp.split(':')][::-1])
                player = self.bot.lavalink.player_manager.get(ctx.guild.id)
                await player.seek(time*1000)
                await ctx.message.add_reaction('<a:PurpleCheck:922496654739902474>')
            except ValueError:
                return await ctx.send('Provided a wrong value')
        else:
            player = self.bot.lavalink.player_manager.get(ctx.guild.id)
            await player.seek(timestamp * 1000)
            await ctx.message.add_reaction('<a:PurpleCheck:922496654739902474>')

    @commands.command()
    async def pause(self, ctx: commands.Context):
        player: lavalink.PlayerManager = self.bot.lavalink.player_manager.get(ctx.guild.id)
        await self.handle_except(player, ctx)
        if not player.paused:
            await player.set_pause(True)
            await ctx.message.add_reaction('<a:PurpleCheck:922496654739902474>')
        else:
            await ctx.send("Nothing is playing right now.")

    @commands.command(aliases=['resume',])
    async def unpause(self, ctx: commands.Context):
        player: lavalink.PlayerManager = self.bot.lavalink.player_manager.get(ctx.guild.id)
        await self.handle_except(player, ctx)
        if player.paused:
            await player.set_pause(False)
            await ctx.message.add_reaction('<a:PurpleCheck:922496654739902474>')
        else:
            await ctx.send("Player is already playing!")


    @commands.command()
    async def stop(self, ctx: commands.Context):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        await self.handle_except(player, ctx)
        player.queue.clear()
        await player.stop()
        await ctx.voice_client.disconnect(force=True)
        await ctx.message.add_reaction('⏹️')

    @commands.command()
    async def skip(self, ctx: commands.Context):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        await self.handle_except(player, ctx)
        await player.skip()
        await ctx.message.add_reaction('<a:PurpleCheck:922496654739902474>')

    @commands.command(aliases=['dc'])
    async def disconnect(self, ctx):
        player = self.bot.lavalink.player_manager.get(ctx.guild.id)
        await self.handle_except(player, ctx)
        player.queue.clear()
        await player.stop()
        await ctx.voice_client.disconnect(force=True)
        await ctx.send('*⃣ | Disconnected.')
        await ctx.message.add_reaction('⏹️')


def setup(bot):
    bot.add_cog(Music(bot))
