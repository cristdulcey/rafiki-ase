from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, String, Text

from database import Base
from helpers.create_key import generate_uuid


class AppKey(Base):
    __tablename__ = "app_keys"

    id: str = Column(String, primary_key=True, index=True, default=generate_uuid)
    name: str = Column(String, nullable=False)
    issuer: str = Column(String, nullable=True)
    audience: str = Column(String, nullable=True)
    secret_key: str = Column(Text, nullable=False)
    is_active: bool = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
