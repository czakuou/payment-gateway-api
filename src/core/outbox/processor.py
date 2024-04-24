from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, Any

from src.core.logging import Logger
from src.core.outbox.model import MessageType
from src.core.outbox.sql_outbox import MessageOutbox

if TYPE_CHECKING:
    from apos import Apos
    from sqlalchemy.ext.asyncio import AsyncSession


class OutboxProcessor:
    def __init__(
        self,
        message_outbox: MessageOutbox,
        session: AsyncSession,
        messenger: Apos,
        logger: Logger,
    ) -> None:
        self._message_outbox = message_outbox
        self._session = session
        self._messenger = messenger
        self._log = logger

    @staticmethod
    def _get_cls_for(message_type: MessageType) -> Any:
        module = importlib.import_module(message_type.module_name())
        return getattr(module, message_type.class_name())

    async def process_outbox_message(self) -> None:
        async with self._session.begin():
            messages = await self._message_outbox.to_publish()

            for message in messages:
                event_cls = self._get_cls_for(message.type)
                event = event_cls(**message.data)
                self._messenger.publish_event(event)
                self._log.info("Publishing event %s", event)
                await self._message_outbox.mark_as_published(message)
