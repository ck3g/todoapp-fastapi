"""Add Note and DueDate to Task

Revision ID: 645828e981e2
Revises: 8c435d265425
Create Date: 2025-01-06 08:02:15.139741

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "645828e981e2"
down_revision: Union[str, None] = "8c435d265425"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "task", sa.Column("note", sa.String(1_000), server_default="", nullable=False)
    )
    op.add_column("task", sa.Column("due_date", sa.Date, index=True))


def downgrade() -> None:
    op.drop_column("task", "due_date")
    op.drop_column("task", "note")
