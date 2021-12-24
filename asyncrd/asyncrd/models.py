from typing import Tuple

class BasicProtocol():    
    def __init__(self, *query : str):
        self.query : Tuple[str] = query

class Set(BasicProtocol):
    command = 'SET'
    def __init__(self, key: str, value: str):
        super().__init__(key, value)

class Get(BasicProtocol):
    command = 'GET'
    def __init__(self, key: str):
        super().__init__(key)

class HSet(BasicProtocol):
    command = 'HSET'
    def __init__(self, base: str, key: str, value: str):
        super().__init__(base, key, value)

class HGet(BasicProtocol):
    command = 'HGET'
    def __init__(self, base: str, key: str):
        super().__init__(base, key)

class HMSet(BasicProtocol):
    command = 'HMSET'
    def __init__(self, base: str, *queries):
        super().__init__(base, *queries)

class HMGet(BasicProtocol):
    command = 'HMGET'
    def __init__(self, base: str, *keys: str):
        super().__init__(base, *keys)

class Delete(BasicProtocol):
    command = 'DEL'
    def __init__(self, *keys: str):
        super().__init__(*keys)



