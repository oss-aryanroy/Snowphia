from typing import Union, List


class Image:
    __slots__ = ('url', 'height', 'width')

    def __init__(self, url: str, height: int, width: int):
        self.url = url
        self.height = height
        self.width = width


class Character:
    def __init__(self, *,
                 image: Image,
                 name: str,
                 description: str,
                 game_description: str,
                 star_rank: str,
                 alternative_names: Union[List[str], str],
                 title: str,
                 vision: str,
                 weapon: str,
                 constellation: str,
                 gender: str,
                 birthday: str,
                 body_type: str,
                 voice_actor_jp: str,
                 voice_actor_eng: str,
                 voice_actor_ch: str,
                 origin: str = None):
        self.image: Image = image
        self.name: str = name
        self.description: str = description
        self.game_description: str = game_description
        self.star_rank: str = star_rank
        self.alternative_names: Union[List[str], str] = alternative_names
        self.title: str = title
        self.vision: str = vision
        self.origin: str = origin
        self.weapon: str = weapon
        self.constellation: str = constellation
        self.gender: str = gender
        self.birthday: str = birthday
        self.body_type: str = body_type
        self.voice_actor_jp: str = voice_actor_jp
        self.voice_actor_en: str = voice_actor_eng
        self.voice_actor_cn: str = voice_actor_ch
