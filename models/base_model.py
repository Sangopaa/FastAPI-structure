import uuid
from uuid import UUID
from sqlmodel import SQLModel, Field, Column, DateTime
from sqlmodel.main import SQLModelMetaclass
from sqlalchemy import ForeignKey

from datetime import datetime, timezone
from typing import Optional


class AutoTableMeta(SQLModelMetaclass):
    def __new__(cls, name, bases, dct, **kwargs):
        if name != "BaseModel":
            if "table" not in kwargs:
                kwargs["table"] = True

            module_name = dct.get("__module__", "")
            if module_name.startswith("models."):
                parts = module_name.split(".")

                if len(parts) >= 3:
                    schema_name = parts[1]

                    table_args = dct.get("__table_args__", {})

                    if isinstance(table_args, dict):
                        if "schema" not in table_args:
                            table_args["schema"] = schema_name
                        dct["__table_args__"] = table_args
                    elif table_args is None:
                        dct["__table_args__"] = {"schema": schema_name}

        return super().__new__(cls, name, bases, dct, **kwargs)


class BaseModel(SQLModel, metaclass=AutoTableMeta):
    id: UUID = Field(
        default_factory=uuid.uuid4, primary_key=True, index=True, nullable=False
    )

    is_deleted: bool = Field(default=False, description="Soft delete flag")
    is_active: bool = Field(default=False, description="Show if the row is available")

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    updated_at: Optional[datetime] = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(
            DateTime(timezone=True),
            onupdate=lambda: datetime.now(timezone.utc),
            nullable=True,
        ),
    )

    created_by: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        description="UUID of the user who created this record",
    )

    updated_by: Optional[UUID] = Field(
        default=None,
        sa_column=Column(
            ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        description="UUID of the user who last updated this record",
    )
