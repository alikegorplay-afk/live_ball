from dataclasses import dataclass, field
from typing import List

from ._typing import ResponseType

@dataclass
class MatchBlock:
    """Резульата получение всех матчей
    
    Args:
        url (str): URL к стриму
        left_team (str): Команда из левой секции
        right_team (str): Команда из правой секции
    """
    url: str
    left_team: str
    right_team: str
    
    def to_dict(self):
        return {
            'url': self.url,
            'left_team': self.left_team,
            'right_team': self.right_team,
            'id': self.id
        }
    
    @property
    def id(self) -> int:
        return int(self.url.split("/")[-1])
    

@dataclass
class LiveMatchResponse:
    """Результат парсинга страницы

    Args:
        url (str): URL к стриму
        title (str): Название транцилясии 
        description (str): Описание матча
        m3u8_url (str | None): Непосредственно ссылка на m3u8 файл
    """
    url: str
    title: str
    description: str
    m3u8_url: str | None = None
    
    def to_dict(self) -> ResponseType:
        return {
            'title': self.title,
            'description': self.description,
            'm3u8_url': self.m3u8_url,
            #'id': self.id
        }
        
    @property
    def id(self) -> int:
        return int(self.url.split("/")[-1])
    
@dataclass
class ParseResult:
    """Резултат получение всех URL-ов

    Args:
        urls (List[MatchBlock]): Все матчи из результата парсинга
    """
    urls: List["MatchBlock"] = field(default_factory=list)
    
    def __iter__(self):
        return iter(self.urls)
    
    def __len__(self):
        return len(self.urls)