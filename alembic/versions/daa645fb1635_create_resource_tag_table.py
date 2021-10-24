"""Create Resource_Tag table

Revision ID: daa645fb1635
Revises: b09473f6e5fa
Create Date: 2021-10-24 13:02:15.248821

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'daa645fb1635'
down_revision = 'b09473f6e5fa'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'resource_tag',
        sa.Column('resource_id', sa.Integer, primary_key=True),
        sa.Column('tag_id', sa.Integer, primary_key=True),
        sa.ForeignKeyConstraint(('resource_id',), ['resource.id']),
        sa.ForeignKeyConstraint(('tag_id',), ['tag.id']),
    )


def downgrade():
    op.drop_table('resource_tag')