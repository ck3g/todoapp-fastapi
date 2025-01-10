from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


class DueDateValidatorMixin:
    @field_validator("due_date")
    @classmethod
    def validate_due_date(cls, value: Any):
        """Ensures that due_date is correct date"""
        if value is None:
            return value

        try:
            parsed_date = datetime.strptime(value, "%Y-%m-%d").date()
            return parsed_date
        except ValueError as exc:
            raise ValueError("Invalid date format. Please use YYYY-MM-DD.") from exc


class CreateTaskRequest(BaseModel, DueDateValidatorMixin):
    title: str = Field(min_length=3, max_length=255)
    note: Optional[str] = Field(default="", max_length=1_000)
    due_date: Optional[str] = None
    completed: Optional[bool] = None
    list_id: Optional[int] = None


class UpdateTaskRequest(BaseModel, DueDateValidatorMixin):
    title: Optional[str] = Field(default=None, min_length=3, max_length=255)
    note: Optional[str] = Field(default="", max_length=1_000)
    due_date: Optional[str] = None
    completed: Optional[bool] = None
    list_id: Optional[int] = None
