from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: Optional[str] = None
    token_type: Optional[str] = None
    client: Optional[str] = None
    iss: Optional[str] = None
    aud: Optional[str] = None
    scope: Optional[str] = None


class RefreshToken(BaseModel):
    refresh_token: str
