class KozumikkuException(Exception):
    """
    The class that all library exceptions inherit from
    """


class HTTPException(KozumikkuException):
    """
    Errors that are raised while performing HTTP requests will be raised
    through this exception or a subclass
    """

    def __init__(self, data, response):
        self.msg = response.reason

        if isinstance(data, dict):
            msg = data.get("message")  # a custom message from the api
            if msg is not None:
                self.msg = msg

        self.status_code = response.status

    def __str__(self) -> str:
        fmt = "{0.status_code}: {0.msg}"
        return fmt.format(self)


class Ratelimited(HTTPException):
    """
    Error raised when we are ratelimited
    """
    pass


class Forbidden(HTTPException):
    """
    Error raised when we get a 403
    """
    pass


class KozumikkuServerError(HTTPException):
    """
    Error raised when we get a 500 or higher
    """
    pass


class NotFound(HTTPException):
    """
    Error raised when we get a 404
    """
    pass


class Unauthorized(HTTPException):
    """
    Error raised when we get a 401
    """
