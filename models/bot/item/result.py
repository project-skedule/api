from pydantic import BaseModel, Field


class Result(BaseModel):
    data: bool
