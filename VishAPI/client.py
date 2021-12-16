import json
import aiohttp
from io import BytesIO
from VishAPI.exceptions import APIException, NotExist
from VishAPI.objects import Character, Image


def handle_exception(response):
    if response.status not in range(200, 299):
        try:
            result = await response.json()
            response = result['message']
            code = result["code"]
        except aiohttp.ContentTypeError:
            response = await response.text()
            code = response.status
        raise APIException(response, status=code)


class GenshinEndpoint:
    __slots__ = ('api_key', 'session', '_key_check')

    def __init__(self, *, api_key: str, session: aiohttp.ClientSession = None) -> None:
        self.api_key: str = api_key
        self._key_check = {
            "character": self.character_arrange_dict,
            "weapon": self.weapon_arrange_dict,
            "artifact": self.artifact_arrange_dict
        }
        self.session: aiohttp.ClientSession = session
        if session and not isinstance(session, aiohttp.ClientSession):
            self.session = None

    @staticmethod
    async def artifact_arrange_dict(json_obj: dict):
        raise NotImplementedError("Requested endpoint has not been developed yet")

    @staticmethod
    async def weapon_arrange_dict(json_obj: dict):
        raise NotImplementedError("Requested endpoint has not been developed yet")

    @staticmethod
    async def character_arrange_dict(json_obj: dict) -> Character:
        initial_dictionary = {}
        image = Image(**json_obj['character_image'])
        initial_dictionary.update({'image': image})
        initial_dictionary.update({'name': json_obj['name']})
        initial_dictionary.update({'description': json_obj['description']})
        initial_dictionary.update({'game_description': json_obj['game_description']})
        initial_dictionary.update(json_obj['character_info'])
        return Character(**initial_dictionary)

    async def request(self, endpoint: str, name: str, **kwargs):
        headers = {"Authorization": self.api_key}
        func = self._key_check.get(endpoint)
        if not func:
            raise NotExist("This endpoint doesn't exist")
        try:
            raw = kwargs.pop("raw")
        except KeyError:
            raw = False
        base_url = f"https://api.kozumikku.tech/genshin/{endpoint}/{name}"
        if not self.session:
            async with aiohttp.ClientSession() as session:
                async with session.get(base_url, params=kwargs, headers=headers) as response:
                    handle_exception(response)
                    json_obj = await response.json()
                    if raw:
                        return json_obj
                    func = self._key_check.get(endpoint)
                    if not func:
                        raise NotExist("This endpoint doesn't exist")
                    return await func(json_obj)
        else:
            async with self.session.get(base_url, params=kwargs, headers=headers) as response:
                handle_exception(response)
                json_obj = await response.json()
                if raw:
                    return json_obj
                return await func(json_obj)


class ImageEndpoint:
    __slots__ = ('api_key', 'session', 'io')

    def __init__(self, *, api_key: str, session: aiohttp.ClientSession = None, io: bool = None) -> None:
        self.api_key: str = api_key
        if io is not None and not isinstance(io, bool):
            raise TypeError("Except bool got", type(io))
        self.io: bool = io
        self.session: aiohttp.ClientSession = session
        if session and not isinstance(session, aiohttp.ClientSession):
            self.session = None

    async def request(self, endpoint: str, **kwargs):
        headers = {"Authorization": self.api_key}
        base_url = f"https://api.kozumikku.tech/image/{endpoint}"
        if not self.session:
            async with aiohttp.ClientSession() as session:
                async with session.get(base_url, params=kwargs, headers=headers) as response:
                    handle_exception(response)
                    bytes_obj = await response.read()
                    if self.io:
                        return BytesIO(bytes_obj)
                    return bytes_obj
        else:
            async with self.session.get(base_url, params=kwargs, headers=headers) as response:
                handle_exception(response)
                bytes_obj = await response.read()
                if self.io:
                    return BytesIO(bytes_obj)
                return bytes_obj
