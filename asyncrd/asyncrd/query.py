from .models import BasicProtocol, Get, Set
from typing import Union
from .exceptions import RedisException
from .encoders import _encode_command_string, _encode_array, _encode_bulk_string, _encode_integer
from redis_protocol import decode as decoder
    
class Route:
    def __init__(self, protocol: Union[Get, Set, BasicProtocol]) -> None:
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

    async def write_data(self, data):
        self.writer.write(data)
        await self.writer.drain()
        
    async def _execute_command(self, protocol) -> str:
        route = Route(protocol)
        data_ = route.format_command(*protocol.query)
        await self.write_data(data_)
        data = await self.reader.read(100)
        return decoder(data.decode('utf-8'))
        
    async def do_query(self, protocol : Union[Get, Set, BasicProtocol]):
        res = await self._execute_command(protocol)
        return res
    
