from typing import Optional, Tuple
import asyncio, socket
from urllib.parse import urlparse
from .models import Query, Get, Set, Delete
from .exceptions import RedisException


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

    async def delete(self, *keys) -> Tuple[bool, str]:
        await self._do_connect_check()
        
        data = Query(self)
        result = await data.do_query(Delete(*keys))
        return result
