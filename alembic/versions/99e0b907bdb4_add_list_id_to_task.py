"""Add list_id to task

Revision ID: 99e0b907bdb4
Revises: d2d6b7c12ea4
Create Date: 2025-01-10 08:23:42.796079

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "99e0b907bdb4"
down_revision: Union[str, None] = "d2d6b7c12ea4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch_alter_table for SQLite compatibility
    with op.batch_alter_table("task", schema=None) as batch_op:
        batch_op.add_column(sa.Column("list_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key("fk_task_list", "list", ["list_id"], ["id"])


def downgrade() -> None:
    # Use batch_alter_table for SQLite compatibility
    with op.batch_alter_table("task", schema=None) as batch_op:
        batch_op.drop_constraint("fk_task_list", type_="foreignkey")
        batch_op.drop_column("list_id")
