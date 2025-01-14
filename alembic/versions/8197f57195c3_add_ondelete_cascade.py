"""Add ondelete CASCADE

Revision ID: 8197f57195c3
Revises: 99e0b907bdb4
Create Date: 2025-01-14 10:13:59.346100

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8197f57195c3"
down_revision: Union[str, None] = "99e0b907bdb4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Use batch_alter_table for SQLite compatibility
    with op.batch_alter_table("list", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "fk_list_user", "user", ["user_id"], ["id"], ondelete="CASCADE"
        )

    with op.batch_alter_table("task", schema=None) as batch_op:
        batch_op.drop_constraint("fk_task_list", type_="foreignkey")
        batch_op.create_foreign_key(
            "fk_task_user", "user", ["user_id"], ["id"], ondelete="CASCADE"
        )
        batch_op.create_foreign_key(
            "fk_task_list", "list", ["list_id"], ["id"], ondelete="CASCADE"
        )


def downgrade() -> None:
    with op.batch_alter_table("task", schema=None) as batch_op:
        batch_op.drop_constraint("fk_task_user", type_="foreignkey")
        batch_op.drop_constraint("fk_task_list", type_="foreignkey")
        batch_op.create_foreign_key("fk_task_user", "user", ["user_id"], ["id"])
        batch_op.create_foreign_key("fk_task_list", "list", ["list_id"], ["id"])

    with op.batch_alter_table("list", schema=None) as batch_op:
        batch_op.drop_constraint("fk_list_user", type_="foreignkey")
        batch_op.create_foreign_key("fk_list_user", "user", ["user_id"], ["id"])
