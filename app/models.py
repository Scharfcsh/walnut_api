from sqlalchemy import Column, Integer, String, Numeric, DateTime
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base
from typing import Optional, Literal
from datetime import timezone
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String, unique=True, nullable=False)

    source_account = Column(String)
    destination_account = Column(String)
    amount = Column(Numeric)
    currency = Column(String)

    status: Mapped[Literal["PROCESSING", "PROCESSED"]] = mapped_column(
        String, default="PROCESSING"
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    processed_at = Column(DateTime(timezone=True), nullable=True)
