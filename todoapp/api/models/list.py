from typing import Optional

from pydantic import BaseModel, Field


class ListRequest(BaseModel):
    title: Optional[str] = Field(min_length=3, max_length=50)
