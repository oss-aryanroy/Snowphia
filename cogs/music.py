import pomice
import discord
from discord.ext import commands


class Music(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.pomice = pomice.NodePool()

    async def start_nodes(self):
        await self.pomice.create_node(bot=self.bot, host='lavalinkonreplit.icerose.repl.co', port='443',
                                      password='asecurepasswordlol', identifier='MAIN',
                                      spotify_client_id=self.bot.spotify_client_id,
                                      spotify_client_secret=self.bot.spotify_client_secret)
        print(f"Node is ready!")

    @commands.command(name='join', aliases=['connect'])
    async def join(self, ctx: commands.Context, *, channel: discord.TextChannel = None) -> None:

        if not channel:
            channel = getattr(ctx.author.voice, 'channel', None)
            if not channel:
                raise commands.CheckFailure('You must be in a voice channel to use this command'
                                            'without specifying the channel argument.')

        await ctx.author.voice.channel.connect(cls=pomice.Player)
        await ctx.send(f'Joined the voice channel `{channel}`')

    @commands.command(name='play')
    async def play(self, ctx, *, search: str) -> None:

        if not ctx.voice_client:
            await ctx.invoke(self.join)

        player = ctx.voice_client

        results = await player.get_tracks(query=f'{search}')

        if not results:
            raise commands.CommandError('No results were found for that search term.')

        if isinstance(results, pomice.Playlist):
            await player.play(track=results.tracks[0])
        else:
            await player.play(track=results[0])


def setup(bot):
    bot.add_cog(Music(bot))
