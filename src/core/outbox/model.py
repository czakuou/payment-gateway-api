from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, override

from src.core.db.models import Base

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.orm import Mapped


@dataclass(frozen=True)
class MessageType:
    qualified_name: str

    def module_name(self) -> str:
        without_class_name = self.qualified_name.split(".")[:-1]
        return ".".join(without_class_name)

    def class_name(self) -> str:
        return self.qualified_name.split(".")[-1]

    @override
    def __str__(self) -> str:
        return self.qualified_name


@dataclass
class OutboxMessage:
    id: str
    occurred_on: datetime
    type: MessageType
    data: dict[str, Any]
    processed_on: datetime | None


class OutboxMessageModel(Base):
    type: Mapped[str]
    data: Mapped[dict[str, str]]
    processed_on: Mapped[datetime | None]

    @override
    def __str__(self) -> str:
        return (
            f"OutboxMessage(id={self.id}, occurred_on={self.created_at}, "
            f"type={self.type}, processed_on={self.processed_on})"
        )
