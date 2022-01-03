from pydantic import BaseModel


class Result(BaseModel):
    data: bool
