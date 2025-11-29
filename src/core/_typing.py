from typing import TypedDict


class ResponseType(TypedDict):
    title: str
    description: str
    m3u8_url: str | None