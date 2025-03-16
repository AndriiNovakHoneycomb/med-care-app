"""added phone and status to users

Revision ID: eac0aa3c22d7
Revises: b889373c9593
Create Date: 2025-03-16 10:18:24.779530

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eac0aa3c22d7'
down_revision = 'b889373c9593'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('phone', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('status', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'status')
    op.drop_column('users', 'phone')
    # ### end Alembic commands ###
