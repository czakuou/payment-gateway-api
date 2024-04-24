from src.core.outbox.event import Event
from src.core.outbox.sql_outbox import MessageOutbox


class StoreAndForwardEventBus:
    def __init__(self, message_outbox: MessageOutbox) -> None:
        self._message_outbox = message_outbox

    def publish(self, event: Event) -> None:
        self._message_outbox.save(event)
