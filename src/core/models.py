import uuid
from datetime import datetime
from typing import Any, ClassVar, Literal, TypeVar, override

from sqlalchemy import JSON, DateTime, ForeignKey, MetaData, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
    relationship,
)
from sqlalchemy.types import TypeEngine


class Base(AsyncAttrs, DeclarativeBase):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )

    type_annotation_map: ClassVar[dict[type, TypeEngine[Any]]] = {
        datetime: DateTime(timezone=True),
        dict[str, str]: JSON(),
    }

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    @declared_attr.directive
    @override
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"


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
