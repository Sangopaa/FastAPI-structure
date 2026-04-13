from typing import Generic, Sequence, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    data: Sequence[T]
    total: int
    skip: int
    limit: int
