from typing import Any


class Database:
    __slots__ = ('connection',)
    def __init__(self, bot) -> None:
        self.connection = bot.pg_con

    async def execute(self, required: str, *args) -> Any:
        pool = self.connection.acquire()
        async with pool as con:
            async with con.transaction():
                result = await con.execute(required, *args)
        return result

    async def fetch(self, required: str, *args) -> Any:
        pool = self.connection.acquire()
        async with pool as con:
            async with con.transaction():
                result = await con.fetch(required, *args)
        return result

    async def fetchval(self, required: str, *args) -> Any:
        pool = self.connection.acquire()
        async with pool as con:
            async with con.transaction():
                result = await con.fetchval(required, *args)
        return result

    async def fetchrow(self, required: str, *args) -> Any:
        pool = self.connection.acquire()
        async with pool as con:
            async with con.transaction():
                result = await con.fetchrow(required, *args)
        return result