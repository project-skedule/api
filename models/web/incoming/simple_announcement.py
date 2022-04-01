from pydantic import BaseModel


class SimpleAnnouncement(BaseModel):
    text: str
