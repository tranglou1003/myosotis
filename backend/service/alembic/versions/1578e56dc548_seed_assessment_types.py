"""seed assessment types

Revision ID: 84c1ccaf2b01
Revises: 69c8b2ad0bfd
Create Date: 2025-09-17 09:02:50.442290

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import datetime


# revision identifiers, used by Alembic.
revision: str = "1578e56dc548"
down_revision: Union[str, None] = "69c8b2ad0bfd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    now = datetime.datetime.utcnow()
    op.execute("""
    INSERT INTO assessment_types (id, name, description, difficulty_level, max_score, passing_score, is_active, created_at, updated_at)
    VALUES 
        (1, 'MMSE', 'Mini-Mental State Examination', 1, 30, 24, TRUE, NOW(), NOW()),
        (2, 'MOCA', 'Montreal Cognitive Assessment', 1, 30, 26, TRUE, NOW(), NOW())
    ON CONFLICT (id) DO NOTHING;
""")


def downgrade() -> None:
    op.execute("""
        DELETE FROM assessment_types WHERE id IN (1, 2);
    """)