"""empty message

Revision ID: 99d25fa87893
Revises: fbb566c27690
Create Date: 2022-03-27 02:10:22.466686

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '99d25fa87893'
down_revision = 'fbb566c27690'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('print_queue', sa.Column('file_name', sa.String(length=120), nullable=False,
                                           server_default='Not Set'))
    # ### end Alembic commands ###

