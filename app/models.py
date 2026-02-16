from sqlalchemy import Column, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.database import Base
from datetime import datetime
import uuid

class Voucher(Base):
    __tablename__ = "vouchers"

    code = Column(String(50), primary_key=True, unique=True, nullable=False)
    discount_percentage = Column(Float, nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<Voucher(code={self.code}, discount_percentage={self.discount_percentage}, active={self.active})>"