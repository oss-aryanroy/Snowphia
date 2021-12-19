import aiohttp
from io import BytesIO
from typing import Optional, Union
from .exceptions import KozumikkuServerError, Forbidden, NotFound, HTTPException, Ratelimited, Unauthorized


async def parse_response(resp: aiohttp.ClientResponse) -> Union[dict, bytes]:
    try:
        data = await resp.json()
    except aiohttp.ContentTypeError:
        data = await resp.read()
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

    async def request(self, route: str, **kwargs):
        self._create_session()
        headers = {"Authorization": self._token}
        async with self.__session.get(route, params=kwargs, headers=headers) as response:
            if response.ok:
                result = await parse_response(response)
                return result
            self.handle_exception(response)
