from .connection import *
from .query import *

async def connect(connection_url : str):
    CONNECTION = ConnectionProtocol(connection_url)
    await CONNECTION.connect()
    return CONNECTION