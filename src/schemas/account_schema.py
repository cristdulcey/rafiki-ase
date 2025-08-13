from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class AccountBase(BaseModel):
    name: str
    path: str


class AccountCreate(AccountBase):
    asset_id: UUID


class AccountUpdate(AccountBase):
    wallet_address_id: Optional[UUID] = None
    wallet_address: Optional[str] = None


class AccountResponse(AccountBase):
    id: UUID
    wallet_address_id: Optional[UUID] = None
    wallet_address: Optional[str] = None
    asset_code: str
    asset_scale: int
    asset_id: UUID

    class Config:
        from_attributes = True


class AccountDetailResponse(AccountBase):
    id: UUID
    wallet_address_id: Optional[UUID] = None
    wallet_address: Optional[str] = None
    asset_code: str
    asset_scale: int
    asset_id: UUID
    liquidity: Optional[int] = None
    status: Optional[str] = None

    class Config:
        from_attributes = True


class AccountListResponse(BaseModel):
    accounts: list[AccountResponse]
    count: int

    class Config:
        from_attributes = True
        validate_by_name = True
        use_enum_values = True


class WithdrawBase(BaseModel):
    wallet_address_id: UUID


class DepositBase(WithdrawBase):
    credit: float = Field(gt=0, description="Amount to deposit, must be greater than 0")


class LinkKeyBase(WithdrawBase):
    key: str = Field(..., description="Key to link to the wallet address")
