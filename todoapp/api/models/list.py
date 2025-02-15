from typing import Optional

from pydantic import BaseModel, Field


class CreateListRequest(BaseModel):
    title: Optional[str] = Field(min_length=3, max_length=50)
    group_id: Optional[int] = None


class UpdateListRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=3, max_length=50)
    group_id: Optional[int] = None
