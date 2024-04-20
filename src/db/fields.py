from __future__ import annotations

from typing import TYPE_CHECKING, Literal, TypeVar

from sqlalchemy import UUID, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    import uuid

    from src.db.models import Base

    Model = TypeVar("Model", bound=Base)


def foreign_key(target: type[Base], ondelete: Literal["CASCADE", "SET NULL"] = "CASCADE") -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), ForeignKey(target.id, ondelete=ondelete))


def parent_relationship(target: type[Model], *, back_populates: str) -> Mapped[Model]:
    return relationship(target, back_populates=back_populates)


def child_relationship(
    target: str, *, back_populates: str, uselist: bool | None = None, order_by: str | None = None
) -> Mapped[list[Model]]:
    return relationship(
        target,
        back_populates=back_populates,
        uselist=uselist,
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by=order_by or f"{target}.id",
    )
