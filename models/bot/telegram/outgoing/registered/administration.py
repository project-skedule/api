from datetime import datetime
from typing import Optional

from models.bot.telegram.outgoing.administration_role import AdministrationRole
from pydantic import BaseModel, Field


class Administration(BaseModel):
    premium_status: int = Field(ge=0, le=255)
    last_payment_data: Optional[datetime]
    subscription_until: Optional[datetime]
    main_role: AdministrationRole
