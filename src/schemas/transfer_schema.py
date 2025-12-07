from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from enums.auth import TransferEnum


class TransferBase(BaseModel):
    wallet_receive_url: str
    amount: float = Field(gt=0, description="Amount to deposit, must be greater than 0")
    wallet_sender_id: UUID
    description: Optional[str] = None


class TransferResponse(BaseModel):
    id: UUID


class InitWallets(BaseModel):
    wallet_receive_url: str
    amount: float = Field(gt=0, description="Amount to deposit, must be greater than 0")
    wallet_sender_id: UUID
    description: Optional[str] = None

class TransferCreateBase(BaseModel):
    type_transfer : TransferEnum = TransferEnum.INCOMING
    sender_wallet_address : str
    receiver_wallet_address : str
    asset_code : str
    amount : float
    description : Optional[str] = None
    transaction_hash : Optional[str] = None