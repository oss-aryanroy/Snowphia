import asyncio, typing
from .exceptions import RedisException
from .parser import Parser
from .encoders import _encode_command_string, _encode_array, _encode_bulk_string, _encode_error, _encode_integer, _encode_simple_string
from redis_protocol import decode as decoder
from redis_protocol import encode as encoder

CRLF = "\r\n"



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
        command_formatted = _encode_command_string(self._protocol.command, lonely=False)
        to_pass_args = [command_formatted,]
        command = self._format_args(to_pass_args, *args)
        return command.encode("utf-8")

    def _format_args(self, to_pass_args, *args):
        for arg in args:
            if isinstance(arg, int):
                parsed_arg = _encode_integer(arg)
            elif isinstance(arg, str):
                parsed_arg = _encode_bulk_string(arg)
            to_pass_args.append(parsed_arg)
        command_string = _encode_array(to_pass_args)
        return command_string

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
        data = await self.reader.read(100)
        return decoder(data.decode('utf-8'))
        
    async def do_query(self, protocol : typing.Union[Get, Set, BasicProtocol]):
        res = await self._execute_command(protocol)
        return res
    
