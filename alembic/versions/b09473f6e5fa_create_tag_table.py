"""Create Tag table

Revision ID: b09473f6e5fa
Revises: a82a95e67904
Create Date: 2021-10-24 13:02:01.314970

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b09473f6e5fa'
down_revision = 'a82a95e67904'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tag',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('engine', sa.String(100), nullable=False),
        sa.Column('description', sa.String),
        sa.Column('percent_match', sa.Integer, nullable=False),
        sa.UniqueConstraint('name', 'engine', name='uix_1')
    )


def downgrade():
    op.drop_table('tag')