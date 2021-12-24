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

class Delete(BasicProtocol):
    command = 'DELETE'
    def __init__(self, *keys: str):
        super().__init__(*keys)