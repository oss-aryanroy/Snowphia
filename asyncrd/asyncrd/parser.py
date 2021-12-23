import aioconsole, io

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
            protocol_list = ['$', "-", "+"]
            if text[0] not in protocol_list:
                raise RedisException("These ({0}) were not present in the result.".format(", ".join(protocol_list)))
            if "-1" in text:
                protocol_list = ['$', '+']
            for i in protocol_list:
                text = text.strip(i)
            text = text.strip(PROTOCOL)
            results = ["ERR ", "WRONGTYPE ", "OK", "-1"]
            if text.startswith(results[0]):
                text = text.strip(results[0])
                if "unknown" in text:
                    raise RedisCommandUnknown(text)
            if text.startswith(results[1]):
                res = results[1]
                text = text.strip(res)
                raise RedisWrongType(text)
            if text.startswith(results[2]):
                res = results[2]
                text = text.strip(res)
                return "OK"
            if text.startswith(results[3]):
                res = results[3]
                text = text.strip(res)
        elif prot == -1:
            raise RedisException("{0} was not present in the result.".format(PROTOCOL))
