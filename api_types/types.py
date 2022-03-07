from typing import List, Optional
from typing_extensions import Annotated
from pydantic import Field

ID = Annotated[int, Field(ge=1, le=2147483647)]
TID = Annotated[int, Field(ge=1, le=9223372036854775807)]
