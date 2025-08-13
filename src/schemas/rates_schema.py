from typing import Optional

from pydantic import BaseModel

from models.webhook import TypeEnumWebhook


class RateSchema(BaseModel):
    base: Optional[str] = 'USD'


class RateResponseSchema(RateSchema):
    rates: dict[str, float]
