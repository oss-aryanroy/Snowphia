class VishExceptions(Exception):
    """Base Exception for the API Wrapper"""


class APIException(VishExceptions):
    def __init__(self, message: str, *, status: int):
        super().__init__(f"{status}: {message}")
        self.message = message
        self.status = status


class NotExist(VishExceptions):
    def __init__(self, message: str):
        super().__init__(message)
