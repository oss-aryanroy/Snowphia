import asyncio, socket
from urllib.parse import urlparse
from .query import Query, Get, Set, BasicProtocol
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
        
    async def close(self):
        if self._closed:
            raise RedisException('Connection is closed.')
            
        self.writer.close()
        await self.writer.wait_closed()
        self._closed = True
        
    async def __aenter__(self):
        try:
            await self.connect()
        except:
            pass
        
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        try:
            await self.close()
        except:
            pass
        
    async def _do_connect_check(self):
        try:
            if not self._connected:
                await self.connect()
        except:
            pass
        
    def create_custom_protocol(self, command: str, query: str):
        protocol = BasicProtocol(query=query)
        protocol.command = command
        
        return protocol
        
    async def get(self, query : str):
        await self._do_connect_check()
        
        data = Query(self)
        result = await data.do_query(Get(query=query))
        return result

    async def set(self, query : str):
        await self._do_connect_check()
        
        data = Query(self)
        result = await data.do_query(Set(query=query))
        return result
