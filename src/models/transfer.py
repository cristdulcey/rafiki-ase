from datetime import datetime

import uuid

from sqlalchemy import Column, Enum, String, DateTime, func

from database import Base
from sqlalchemy.dialects.postgresql import UUID

from enums.auth import TransferEnum


class Transfer(Base):
    __tablename__ = "transfer"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type_transfer = Column(Enum(TransferEnum), default=TransferEnum.INCOMING, nullable=False)
    sender_wallet_address = Column(String, nullable=False)
    receiver_wallet_address = Column(String, nullable=False)
    asset_code = Column(String, nullable=False)
    amount = Column(String, nullable=False)
    description = Column(String, nullable=True)
    transaction_hash = Column(String, nullable=True)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
