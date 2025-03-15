"""add metadata field to medical_documents

Revision ID: 2a3b4c5d6e7f
Revises: 1a2b3c4d5e6f
Create Date: 2024-02-14 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '2a3b4c5d6e7f'
down_revision = '1a2b3c4d5e6f'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('medical_documents',
        sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=True)
    )

def downgrade():
    op.drop_column('medical_documents', 'metadata') 