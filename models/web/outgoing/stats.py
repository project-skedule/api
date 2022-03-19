from typing import Dict, List

from pydantic import BaseModel, Field


class Statistics(BaseModel):
    data: Dict[int, int]
