from .http import HTTPClient
import aiohttp
from io import BytesIO
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
        image = Image(**json_obj['character_image'])
        return Character(image=image, name=json_obj["name"],
                         description=json_obj["description"],
                         game_description=json_obj["game_description"],
                         **json_obj["character_info"])

    async def request(self, endpoint: str, name: str, **kwargs):
        func = self._key_check.get(endpoint)
        raw = kwargs.pop('raw', False)
        base_url = f"https://api.kozumikku.tech/genshin/{endpoint}/{name}"
        response = await self.http.request(base_url)
        if raw:
            return response
        return func(response)


class ImageEndpoint:
    __slots__ = ('http', 'session', 'io')

    def __init__(self, *, api_key: str, session: aiohttp.ClientSession = None, io: bool = False) -> None:
        """
        Helper class for getting Manipulated Image from Kozumikku API
        """
        self.handle_invalid_argument(io, session)
        self.io: bool = io
        self.http = HTTPClient(api_key, session=session)

    @staticmethod
    def handle_invalid_argument(io, session):
        if io is not None and not isinstance(io, bool):
            raise TypeError("Excepted bool, got", type(io))
        if session and not isinstance(session, aiohttp.ClientSession):
            raise TypeError("An Improper session was passed.")

    @staticmethod
    async def _create_session():
        session = aiohttp.ClientSession()
        return session

    async def request(self, endpoint: str, **kwargs):
        base_url = f"https://api.kozumikku.tech/image/{endpoint}"
        kwargs.update({'io': self.io})
        response = await self.http.request(base_url, **kwargs)
        if self.io:
            response = BytesIO(response)
        return response
