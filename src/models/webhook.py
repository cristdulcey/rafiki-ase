from enum import Enum


class TypeEnumWebhook(str, Enum):
    INCOMING_CREATED = "incoming_payment.created"
    INCOMING_COMPLETED = "incoming_payment.completed"
    INCOMING_EXPIRED = "incoming_payment.expired"
    OUTGOING_CREATED = "outgoing_payment.created"
    OUTGOING_COMPLETED = "outgoing_payment.completed"
    OUTGOING_FAILED = "outgoing_payment.failed"
    WALLET_NOT_FOUND = "wallet_address.not_found"
    ASSET_LIQUIDITY_LOW = "asset.liquidity_low"
    PEER_LIQUIDITY_LOW = "peer.liquidity_low"
    WALLET_ADDRESS_WEB_MONETIZATION = "wallet_address.web_monetization"
