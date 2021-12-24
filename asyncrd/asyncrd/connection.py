import asyncio
from .models import (
    Get,
    HSet,
    HGet,
    HMGet,
    HMSet,
    Set, 
    Delete
)

from .query import Query
from .exceptions import RedisException

from typing import List, Optional, Tuple, Union
from urllib.parse import urlparse


class ConnectionProtocol():
    def __init__(self, connection_url : str):
        self.connection_url = urlparse(connection_url)
        self.hostname = self.connection_url.hostname
        self.port = self.connection_url.port
        
        self.reader = None
        self.writer = None
        
        self._closed = False
        self._connected = False

    async def connect(self):
        if self._connected:
            raise RedisException('Connected to redis database.')
        self.reader, self.writer = await asyncio.open_connection(self.hostname, self.port)
        self._connected = True
        
    async def close(self) ->None:
        if self._closed:
            raise RedisException('Connection is closed.')
            
        self.writer.close()
        await self.writer.wait_closed()
        self._closed = True
        
    async def __aenter__(self) -> None:
        try:
            await self.connect()
        except:
            pass
        
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        try:
            await self.close()
        except:
            pass
        
    async def _do_connect_check(self) -> None:
        try:
            if not self._connected:
                await self.connect()
        except:
            pass

    async def get(self, query : str) -> Optional[str]:
        await self._do_connect_check()
        
        data = Query(self)
        result = await data.do_query(Get(query))
        return result

    async def set(self, key: str, value: str) -> Tuple[bool, str]:
        await self._do_connect_check()
        
        data = Query(self)
        result = await data.do_query(Set(key, value))
        return result

    async def delete(self, *keys) -> bool:
        await self._do_connect_check()
        
        data = Query(self)
        result = await data.do_query(Delete(*keys))
        return bool(result[0])

    async def hset(self, base: str, key: str, value: str) -> bool:
        await self._do_connect_check()
        
        data = Query(self)
        result = await data.do_query(HSet(base, key, value))
        return bool(result[0])

    async def hget(self, base: str, key: str) -> Optional[Union[str, int, list, tuple, dict]]:
        await self._do_connect_check()
        
        data = Query(self)
        result = await data.do_query(HGet(base, key))
        return result

    async def hmset(self, base: str, *queries) -> List[bool]:
        await self._do_connect_check()
        
        data = Query(self)
        result = await data.do_query(HMSet(base, *queries))
        return result

    async def hmget(self, base: str, *queries) -> Optional[Union[str, int, list, tuple, dict]]:
        await self._do_connect_check()
        
        data = Query(self)
        result = await data.do_query(HMGet(base, *queries))
        return result
