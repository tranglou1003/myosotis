"""add video to storytype enum

Revision ID: 69c8b2ad0bfd
Revises: 4ab959c174ea
Create Date: 2025-08-12 23:15:07.327860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69c8b2ad0bfd'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Thêm giá trị 'video' vào enum storytype
    op.execute("ALTER TYPE storytype ADD VALUE IF NOT EXISTS 'video'")


def downgrade():
    # PostgreSQL không hỗ trợ xóa giá trị enum, nên downgrade chỉ ghi chú
    op.execute("""
    -- Can't remove value from enum in PostgreSQL
    """)