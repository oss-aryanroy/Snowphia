import os
import asyncio
import aioredis
import asyncpg
import config
import aiohttp
import discord
from typing import Optional
from utils.cmds import Cached
from utils.context import CustomContext
from utils.buttons import PrefixConfirm
from discord.ext import commands
from jishaku.codeblocks import codeblock_converter

async def get_prefix(bot, message: discord.Message):
    await bot.wait_until_ready()
    request = bot.check_for_cache(message.guild)
    if request == 1:
        prefix = await bot.make_cache_request(message)
    elif request == 2:
        prefix = "sn!"
    else:
        prefix = request
    return prefix
    
    
class SnowBot(commands.AutoShardedBot):
    __slots__ = ('theme', 'redis', 'pg_con', 'spotify_client_id', 'spotify_client_secret', 'cache', 'spotify_session')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme = 0xb1e6fc
        self.redis = aioredis.StrictRedis(decode_responses=True)
        self.pg_con = None
        self.spotify_client_id = config.SPOTIFY_CLIENT_ID
        self.spotify_client_secret = config.SPOTIFY_CLIENT_SECRET
        self.cache = {}
        self.spotify_session = None

    def update_cache(self, guild: discord.Guild, prefix: str = None):
        try:
            self.cache[guild.id].prefix = prefix
        except KeyError:
            self.input_cache(guild, prefix)

    def input_cache(self, guild: discord.Guild, prefix: str = None):
        self.cache[guild.id] = Cached(prefix)

    def check_for_cache(self, guild: discord.Guild):
        object_ = self.cache.get(guild.id, 0)
        if object_ == 0:
            return 1
        prefix = object_.prefix
        return 2 if not prefix else prefix

    async def make_cache_request(self, message):
        prefix = await self.make_request(message)
        if not prefix:
            self.input_cache(message.guild)
            return "sn!"
        self.input_cache(message.guild, prefix)
        return prefix

    async def make_request(self, message: discord.Message):
        pool = self.pg_con.acquire()
        async with pool as session:
            prefix = await session.fetchrow("SELECT * FROM guild_info WHERE guild_id = $1", message.guild.id)
            if not prefix:
                value = False
            else:
                value = prefix.get('prefix')
        return value

    async def start(self, *args, **kwargs):
        async with aiohttp.ClientSession() as self.session:
            await super().start(*args, **kwargs)

    async def get_context(self, message, *, cls=CustomContext):
        return await super().get_context(message, cls=cls)

    async def create_db_pool(self):
        self.pg_con = await asyncpg.create_pool(**config.CREDENTIALS)

    async def startup_task(self) -> None:
        await self.wait_until_ready()
        guild_id, channel_id, message_id, variable = [int(var) for var in
                                                      await self.redis.hmget("restart", "guild_id", "channel_id",
                                                                             "message_id", "to_send")]
        if not variable:
            return
        elif int(variable) == 0:
            return
        await self.redis.hset("restart", "to_send", 0)
        embed = discord.Embed(title="Restarted", description="Bot has restarted successfully!")
        guild = self.get_guild(guild_id)
        channel = guild.get_channel(channel_id)
        message = channel.get_partial_message(message_id)
        await message.edit(embed=embed)

    os.environ["JISHAKU_NO_DM_TRACEBACK"] = "False"
    os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
    os.environ["JISHAKU_HIDE"] = "True"
    os.environ["JISHAKU_RETAIN"] = "True"

    async def on_ready(self):
        print('-' * 25)
        print(f"{client} is now online!")
        print('-' * 25)

    def __str__(self):
        return client.user.name


intents = discord.Intents.all()
client = SnowBot(command_prefix=get_prefix,
                 intents=intents,
                 slash_commands=True)
client.debugger = False


@client.command(hidden=True)
async def debugger(ctx: CustomContext, value: bool):
    client.debugger = value
    return await ctx.reply(f"{'Activated' if value else 'Unactivated'} Debugging mode")


@debugger.error
async def debugger_error(ctx: CustomContext, error: commands.CommandError):
    if isinstance(error, commands.BadArgument):
        print("Something went wrong...")
        print(str(error))


@client.command(hidden=True)
@commands.is_owner()
async def cleanup(ctx: CustomContext, amount: int = 10):
    def check(m):
        return m.author == client.user

    await ctx.channel.purge(limit=amount, bulk=False, check=check)


@client.command(hidden=True)
@commands.is_owner()
async def restart(ctx: CustomContext):
    await client.redis.hset("restart", "guild_id", ctx.guild.id)
    await client.redis.hset("restart", "channel_id", ctx.channel.id)
    embed = discord.Embed(title="Restarting...", description="Hold on, restarting the bot!")
    message = await ctx.reply(embed=embed, mention_author=False)
    await client.redis.hset("restart", "message_id", message.id)
    await client.redis.hset("restart", "to_send", 1)
    await client.close()

@client.command()
@commands.has_permissions(manage_guild=True)
async def setprefix(ctx: CustomContext, string: Optional[str]):  
    if string == ctx.prefix:
        return await ctx.reply(f'Mention a new prefix, `{ctx.prefix}` is your current prefix...')
    request = client.check_for_cache(ctx.guild)
    if not string:
        if request == 2:
            line = f"You are currently using the default prefix `{ctx.prefix}`"
            return await ctx.reply(line, mention_author=False)
        else:
            line = f"The current prefix for this server is `{request}`, reset it to default?"
            view = PrefixConfirm(ctx, None)
            view.message = await ctx.reply(line, view=view, mention_author=False)
        return
    view = PrefixConfirm(ctx, string)
    if request == 2:
        line = f"You are currently using the default prefix `{ctx.prefix}`, switch to `{string}`?"
        view.message = await ctx.reply(line, mention_author=False, view=view)
    else:
        line = f"You are currently using `{ctx.prefix}` as your prefix, switch to `{string}`?"
        view.message = await ctx.reply(line, mention_author=False, view=view)

@client.command(hidden=True, aliases=['update',])
@commands.is_owner()
async def gitpull(ctx: CustomContext):
    command = client.get_command('jsk sh')
    await ctx.invoke(command, argument=codeblock_converter("sudo git pull"))
    await asyncio.sleep(2.0)
    command = client.get_command('restart')
    await ctx.invoke(command)


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

try:
    client.loop.run_until_complete(client.create_db_pool())
    client.loop.create_task(client.startup_task())
    client.run(config.TOKEN)
except discord.LoginFailure:
    print('Looks like The bot failed to log in.')