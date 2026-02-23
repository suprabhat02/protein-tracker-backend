from typing import Any, Generic, TypeVar
from pydantic import BaseModel


T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total: int


class ErrorPayload(BaseModel):
    code: str
    message: str
    details: dict[str, Any] | None = None


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T
    meta: PaginationMeta | None = None


class ApiErrorResponse(BaseModel):
    success: bool = False
    error: ErrorPayload
