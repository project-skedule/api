from typing import List
from config import BaseModel
from pydantic import Field


class Tags(BaseModel):
    data: List[str]
