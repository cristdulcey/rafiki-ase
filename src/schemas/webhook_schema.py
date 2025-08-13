from typing import Optional

from pydantic import BaseModel

from models.webhook import TypeEnumWebhook


class MetaDataWebHook(BaseModel):
    description: Optional[str] = None


class IncomingWebHook(BaseModel):
    value: Optional[str] = None
    assetCode: Optional[str] = None
    assetScale: Optional[int] = 2


class WalletAddressWebHook(BaseModel):
    id: Optional[str] = None
    createdAt: Optional[str] = None
    receivedAmount: Optional[IncomingWebHook] = None


class DataWebHook(BaseModel):
    id: Optional[str] = None
    walletAddressId: Optional[str] = None
    walletAddressUrl: Optional[str] = None
    walletAddress: Optional[WalletAddressWebHook] = None
    client: Optional[str] = None
    receiver: Optional[str] = None
    createdAt: Optional[str] = None
    expiresAt: Optional[str] = None
    incomingAmount: Optional[IncomingWebHook] = None
    receivedAmount: Optional[IncomingWebHook] = None
    debitAmount: Optional[IncomingWebHook] = None
    receiveAmount: Optional[IncomingWebHook] = None
    sentAmount: Optional[IncomingWebHook] = None
    completed: Optional[bool] = None
    updatedAt: Optional[str] = None
    balance: Optional[str] = None
    peerId: Optional[str] = None
    tenantId: Optional[str] = None
    metadata: Optional[MetaDataWebHook] = None
    stateAttempts: Optional[int] = None


class WebHook(BaseModel):
    id: str
    type: TypeEnumWebhook
    data: Optional[DataWebHook] = None
