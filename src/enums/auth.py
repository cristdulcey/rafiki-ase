import enum


class TransferEnum(str, enum.Enum):
    INCOMING = "incoming"
    OUTGOING = "outgoing"
    TRANSFER = "transfer"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"
    TOP_UP = "top-up"
    FEE = "fee"