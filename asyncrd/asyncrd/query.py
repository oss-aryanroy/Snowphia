import asyncio, typing
from .exceptions import CatchException, RedisException
from .parser import Parser
from redis_protocol import decode as decoder
from redis_protocol import encode as encoder

class Result():
    def __init__(self, result : str):
        self.result : str = result          
    
class BasicProtocol():    
    def __init__(self, query : str):
        self.query : str = query

class Set(BasicProtocol):
    command = 'SET'
            
class Get(BasicProtocol):
    command = 'GET'

class Query():
    def __init__(self, connection):
        self.reader = connection.reader
        self.writer = connection.writer
        
    async def _execute_command(self, command: str, query : str):
        parser = Parser()
        data_ = encoder(command, query)
        print(data_)
        data_ = data_.encode()
        self.writer.write(data_)
        await self.writer.drain()
        data = await self.reader.read(100)
        res = data
        res = res.decode("utf-8")
        catching = CatchException(text=res)
        catched = await catching.catch_error()
        return catched
        
    async def do_query(self, protocol : typing.Union[Get, Set, BasicProtocol]):
        command = getattr(protocol, 'command', None)
        res = await self._execute_command(command, protocol.query)
        if res.startswith("$"):
            pass
        return res
    
