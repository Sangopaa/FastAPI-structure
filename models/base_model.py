import uuid
from uuid import UUID
from sqlmodel import SQLModel, Field
from sqlmodel.main import SQLModelMetaclass


class AutoTableMeta(SQLModelMetaclass):
    def __new__(cls, name, bases, dct, **kwargs):
        if name != "BaseModel":
            if "table" not in kwargs:
                kwargs["table"] = True

            # module format: models.subfolder.filename
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
