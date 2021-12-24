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
    def __init__(self, query: str):
        super().__init__(query)
            
class Get(BasicProtocol):
    command = 'GET'
    def __init__(self, query: str):
        super().__init__(query)



class Route:
    def __init__(self, protocol: typing.Union[Get, Set, BasicProtocol]) -> None:
        self._protocol = protocol

    def format_command(self, *args):
        if not args:
            raise RedisException('No arguments were passed for {}'.format(self._protocol.command))
        command_formatted = "{0} {1}".format(self._protocol.command, " ".join(args))
        command = encoder(command_formatted)
        return command.encode()

class Query():
    def __init__(self, connection):
        self.reader = connection.reader
        self.writer = connection.writer
        
    async def _execute_command(self, protocol):
        parser = Parser()
        route = Route(protocol)
        data_ = route.format_command(protocol.query)
        self.writer.write(data_)
        await self.writer.drain()
        data = await self.reader.read()
        return decoder(data.decode())
        
    async def do_query(self, protocol : typing.Union[Get, Set, BasicProtocol]):
        res = await self._execute_command(protocol)
        return res
    
