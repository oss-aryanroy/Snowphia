import os
import asyncio
import aioredis
import config
import aiohttp
import discord
from discord.ext import commands
from jishaku.codeblocks import codeblock_converter


class SnowBot(commands.AutoShardedBot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme = 0xb1e6fc
        self.redis = aioredis.StrictRedis(decode_responses=True)
        self.spotify_client_id = config.SPOTIFY_CLIENT_ID
        self.spotify_client_secret = config.SPOTIFY_CLIENT_SECRET
        self.spotify_session = None

    async def start(self, *args, **kwargs):
        async with aiohttp.ClientSession() as self.session:
            await super().start(*args, **kwargs)

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


async def get_prefix(bot: SnowBot, message: discord.Message):
    if client.debugger and await bot.is_owner(message.author):
        return ['', 'sn!']
    else:
        return ['sn!',]


intents = discord.Intents.all()
client = SnowBot(command_prefix=get_prefix,
                 intents=intents,
                 slash_commands=True)
client.debugger = False


@client.command(hidden=True)
async def debugger(ctx: commands.Context, value: bool):
    client.debugger = value
    return await ctx.reply(f"{'Activated' if value else 'Unactivated'} Debugging mode")


@debugger.error
async def debugger_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.BadArgument):
        print("Something went wrong...")
        print(str(error))


@client.command(hidden=True)
@commands.is_owner()
async def cleanup(ctx: commands.Context, amount: int = 10):
    def check(m):
        return m.author == client.user

    await ctx.channel.purge(limit=amount, bulk=False, check=check)


@client.command(hidden=True)
@commands.is_owner()
async def restart(ctx: commands.Context):
    await client.redis.hset("restart", "guild_id", ctx.guild.id)
    await client.redis.hset("restart", "channel_id", ctx.channel.id)
    embed = discord.Embed(title="Restarting...", description="Hold on, restarting the bot!")
    message = await ctx.reply(embed=embed, mention_author=False)
    await client.redis.hset("restart", "message_id", message.id)
    await client.redis.hset("restart", "to_send", 1)
    await client.close()


@client.command(hidden=True)
@commands.is_owner()
async def gitpull(ctx: commands.Context):
    command = client.get_command('jsk sh')
    await ctx.invoke(command, argument=codeblock_converter("sudo git pull"))
    await asyncio.sleep(2.0)
    command = client.get_command('restart')
    await ctx.invoke(command)


for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')

try:
    client.loop.create_task(client.startup_task())
    client.run(config.TOKEN)
except discord.LoginFailure:
    print('Looks like The bot failed to log in.')