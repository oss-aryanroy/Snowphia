import aioconsole, io
import re

class BaseRedisException(Exception):
    pass

class RedisException(BaseRedisException):
    def __init__(self, message : str):
        super().__init__(message)
        
class RedisCommandUnknown(BaseRedisException):
    def __init__(self, message : str):
        super().__init__(message)
        
class RedisWrongType(BaseRedisException):
    def __init__(self, message : str):
        super().__init__(message)

PROTOCOL = "\r\n"

class Parser():
    async def encoded(self, command, query):
        res = f"*2{PROTOCOL}$4{PROTOCOL}{command}{PROTOCOL}{query}{PROTOCOL}".encode()
        if command == "GET":
            res = f"*1{PROTOCOL}$4{PROTOCOL}{command}{PROTOCOL}{query}{PROTOCOL}".encode()
        return res
    
    def decoded(self, text):
        text = text.decode("utf-8")
        prot = 0
        if prot == 0:
            regex = "(\${1}[0-9])"
            found = re.findall(regex, text)
            if found:
                text.strip(found[0])
            else:
                raise RedisException("Not Valid")
            return text
        elif prot == -1:
            raise RedisException("{0} was not present in the result.".format(PROTOCOL))
