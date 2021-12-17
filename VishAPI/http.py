import aiohttp
from io import BytesIO
from typing import Optional
from .exceptions import KozumikkuServerError, Forbidden, NotFound, HTTPException, Ratelimited, Unauthorized


async def parse_response(resp: aiohttp.ClientResponse, *, io=False, raw=Fals) -> Union[dict, bytes]:
    try:
        data = await resp.json()
    except aiohttp.ContentTypeError:
        data = await resp.read()
        if io:
            data = BytesIO(data)
    return data


class HTTPClient:
    __slots__ = ('_token', '__session')

    def __init__(self, token: str, session: Optional[aiohttp.ClientSession] = None):
        self.__session = session
        self._token = token

    def _create_session(self) -> Optional[aiohttp.ClientSession]:
        if not self.__session or self.__session.closed:
            session = aiohttp.ClientSession()
            self.__session = session
            return session
        return None

    @staticmethod
    def handle_exception(resp: aiohttp.ClientResponse):
        if resp.status == 404:
            raise NotFound(data, resp)
        elif resp.status >= 500:
            raise KozumikkuServerError(data, resp)
        elif resp.status == 403:
            raise Forbidden(data, resp)
        elif resp.status == 429:
            raise Ratelimited(data, resp)
        elif resp.status == 401:
            raise Unauthorized(data, resp)
        else:
            raise HTTPException(data, resp)

    async def request(self, url: str, **kwargs):
        self._create_session()
        raw = kwargs.pop('raw', False)
        io = kwargs.pop('io', False)
        headers = {"Authorization": self._token}
        async with self.__session.get(url, params=kwargs, headers=headers) as response:
            if resp.ok:
                result = parse_response(response, io=io, raw=raw)
                return result
            self.handle_exception(response)
