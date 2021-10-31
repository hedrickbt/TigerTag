"""Create Resource table

Revision ID: a82a95e67904
Revises: 
Create Date: 2021-10-24 13:01:50.772452

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a82a95e67904'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'resource',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=False),
        sa.Column('location', sa.String, nullable=False),
        sa.Column('hashval', sa.String, nullable=False),
        sa.Column('last_indexed', sa.DateTime, nullable=False),
        sa.Column('description', sa.String),
        sa.UniqueConstraint('location', name='uix_1'),
        sa.Index('idx_location', 'location', unique=True)
    )


def downgrade():
    op.drop_table('resource')
