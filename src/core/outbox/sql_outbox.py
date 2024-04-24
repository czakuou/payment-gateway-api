from __future__ import annotations

from dataclasses import asdict
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import select

from src.core.outbox.event import Event
from src.core.outbox.model import MessageType, OutboxMessage, OutboxMessageModel

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class MessageOutbox:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _to_outbox_message(model: OutboxMessageModel) -> OutboxMessage:
        return OutboxMessage(
            id=str(model.id),
            occurred_on=model.created_at,
            type=MessageType(model.type),
            data=model.data,
            processed_on=model.processed_on,
        )

    def save(self, event: Event) -> None:
        data = asdict(event)
        outbox_message = OutboxMessageModel(
            type=f"{type(event).__module__}.{type(event).__name__}",
            data=data,
        )
        self._session.add(outbox_message)

    async def to_publish(self) -> list[OutboxMessage]:
        query = (
            select(OutboxMessageModel)
            .where(OutboxMessageModel.processed_on == None)  # noqa: E711
            .order_by(OutboxMessageModel.created_at.asc())
            .limit(100)
        )

        models = await self._session.scalars(query)
        results = models.all()
        return [self._to_outbox_message(model) for model in results]

    async def mark_as_published(self, message: OutboxMessage) -> None:
        await self._session.merge(
            OutboxMessageModel(
                id=str(message.id),
                occurred_on=message.occurred_on,
                type=str(message.type),
                data=message.data,
                processed_on=datetime.now(UTC),
            )
        )
