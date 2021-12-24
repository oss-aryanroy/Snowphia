class BaseRedisException(Exception):
    pass

class RedisOK(BaseRedisException):
    def __init__(self, message : str):
        self.msg = message

class RedisException(BaseRedisException):
    def __init__(self, message : str):
        super().__init__(message)
        
class RedisCommandUnknown(BaseRedisException):
    def __init__(self, message : str):
        super().__init__(message)
        
class RedisWrongType(BaseRedisException):
    def __init__(self, message : str):
        super().__init__(message)

            
        
