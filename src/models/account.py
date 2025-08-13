from sqlalchemy import Column, String, Integer

from database import Base
from helpers.create_key import generate_uuid


class Account(Base):
    __tablename__ = "account"

    id: str = Column(String, primary_key=True, index=True, default=generate_uuid)
    name: str = Column(String)
    path: str = Column(String)
    wallet_address_id: str = Column(String, index=True)
    wallet_address: str = Column(String, index=True)
    asset_code: str = Column(String)
    asset_scale: int = Column(Integer)
    asset_ledger: int = Column(Integer)
    asset_id: str = Column(String)
    public_key: str = Column(String)
    private_key: str = Column(String)
