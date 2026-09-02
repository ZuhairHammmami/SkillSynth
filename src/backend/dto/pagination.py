"""Pagination DTO — shared request/response schemas for list endpoints."""
import math
from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Query parameters for paginated list endpoints."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=200)


def paginate(items: list, page: int, page_size: int) -> dict:
    """Slice items and return the standard pagination envelope."""
    total = len(items)
    pages = math.ceil(total / page_size) if total > 0 else 1
    start = (page - 1) * page_size
    end = start + page_size
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
    }
