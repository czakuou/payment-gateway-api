from __future__ import annotations

from enum import StrEnum, auto
from typing import TYPE_CHECKING, override

from src.core.db.models import Base

if TYPE_CHECKING:
    from datetime import datetime
    from decimal import Decimal


class CheckoutPaymentStatus(StrEnum):
    SUCCEEDED = auto()
    FAILED = auto()
    PENDING = auto()


class Checkout(Base):
    session_id: str
    status: CheckoutPaymentStatus
    amount: Decimal


class OutboxMessage(Base):
    type: str
    data: dict[str, str]
    processed_on: datetime

    @override
    def __str__(self) -> str:
        return (
            f"OutboxMessage(id={self.id}, occurred_on={self.created_at}, "
            f"type={self.type}, processed_on={self.processed_on})"
        )
