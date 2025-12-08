from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AppKeyBase(BaseModel):
    name: str = Field(..., description="Nombre identificador de la app")
    issuer: Optional[str] = Field(None, description="Issuer esperado en el token")
    audience: Optional[str] = Field(None, description="Audience esperado en el token")
    is_active: Optional[bool] = Field(True, description="Habilita/deshabilita la llave")


class AppKeyCreate(AppKeyBase):
    pass


class AppKeyUpdate(BaseModel):
    name: Optional[str] = None
    issuer: Optional[str] = None
    audience: Optional[str] = None
    is_active: Optional[bool] = None


class AppKeyResponse(AppKeyBase):
    id: UUID
    secret_key: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AppKeyListResponse(BaseModel):
    items: list[AppKeyResponse]
    count: int

    class Config:
        from_attributes = True
