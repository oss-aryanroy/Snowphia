from .http import HTTPClient
import aiohttp
from io import BytesIO
from VishAPI.exceptions import APIException, NotExist
from VishAPI.objects import Character, Image


class GenshinEndpoint:
    __slots__ = ('http', 'session', '_key_check')

    def __init__(self, *, api_key: str, session: aiohttp.ClientSession = None) -> None:
        """
        Helper class for getting Genshin Impact object Information from Kozumikku API
        """

        self._key_check: dict = {
            "character": self.character_arrange_dict,
            "weapon": self.weapon_arrange_dict,
            "artifact": self.artifact_arrange_dict
        }
        self.http = HTTPClient(api_key, session=session)

    @staticmethod
    async def artifact_arrange_dict(json_obj: dict) -> None:
        raise NotImplementedError("Requested endpoint has not been developed yet")

    @staticmethod
    async def weapon_arrange_dict(json_obj: dict) -> None:
        raise NotImplementedError("Requested endpoint has not been developed yet")

    @staticmethod
    def character_arrange_dict(json_obj: dict) -> Character:
        initial_dictionary = {}
        image = Image(**json_obj['character_image'])
        initial_dictionary.update({'image': image})
        initial_dictionary.update({'name': json_obj['name']})
        initial_dictionary.update({'description': json_obj['description']})
        initial_dictionary.update({'game_description': json_obj['game_description']})
        initial_dictionary.update(json_obj['character_info'])
        return Character(**initial_dictionary)

    async def request(self, endpoint: str, name: str, **kwargs):
        func = self._key_check.get(endpoint)
        if not func:
            raise NotExist("This endpoint doesn't exist")
        raw = kwargs.pop('raw', False)
        base_url = f"https://api.kozumikku.tech/genshin/{endpoint}/{name}"
        response = await self.http.request(base_url, raw=raw)
        if raw:
            return response
        return func(response)


class ImageEndpoint:
    __slots__ = ('http', 'session', 'io')

    def __init__(self, *, api_key: str, session: aiohttp.ClientSession = None, io: bool = False) -> None:
        """
        Helper class for getting Manipulated Image from Kozumikku API
        """
        if io is not None and not isinstance(io, bool):
            raise TypeError("Excepted bool got", type(io))
        self.io: bool = io
        self.http = HTTPClient(api_key, session=session)

    @staticmethod
    async def _create_session():
        session = aiohttp.ClientSession()
        return session

    async def request(self, endpoint: str, **kwargs):
        base_url = f"https://api.kozumikku.tech/image/{endpoint}"
        response = await self.http.request(base_url, **kwargs)
        return response
