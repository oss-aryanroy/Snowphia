from .models import BasicProtocol, Get, Set, HGet, HSet, HMGet, HMSet, Delete
from typing import Union
from .exceptions import RedisException
from .encoders import format_command_string, encode_list, encode_string, encode_number
from redis_protocol import decode as decoder
    
class Route:
    def __init__(self, protocol: Union[BasicProtocol, Get, Set, HGet, HSet, HMGet, HMSet, Delete]) -> None:
        self._protocol = protocol

    def format_command(self, *args):
        if not args:
            if self._protocol.command != "QUIT":
                raise RedisException('No arguments were passed for {}'.format(self._protocol.command))
            command = format_command_string(self._protocol.command)
            return command.encode('utf-8')

        command_formatted = format_command_string(self._protocol.command, lonely=False)
        to_pass_args = [command_formatted,]
        command = self._format_args(to_pass_args, *args)
        return command.encode("utf-8")

    def _format_args(self, to_pass: list, *arguments: list):
        for argument in arguments:
            if isinstance(argument, int):
                return_arg = encode_number(argument)
            elif isinstance(argument, str):
                return_arg = encode_string(argument)
            to_pass.append(return_arg)
        command_string = encode_list(to_pass)
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
        
    async def do_query(self, protocol : Union[BasicProtocol, Get, Set, HGet, HSet, HMGet, HMSet, Delete]):
        res = await self._execute_command(protocol)
        return res
    
