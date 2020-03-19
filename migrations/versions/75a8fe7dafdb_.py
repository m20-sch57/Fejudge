"""empty message

Revision ID: 75a8fe7dafdb
Revises: 37fc317ae18b
Create Date: 2020-03-19 14:40:36.461130

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '75a8fe7dafdb'
down_revision = '37fc317ae18b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contest', schema=None) as batch_op:
        batch_op.add_column(sa.Column('owner_id', sa.Integer(), nullable=True))
        batch_op.alter_column('duration',
               existing_type=sa.DATETIME(),
               type_=sa.Interval(),
               existing_nullable=True)
        batch_op.create_foreign_key(None, 'user', ['owner_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('contest', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.alter_column('duration',
               existing_type=sa.Interval(),
               type_=sa.DATETIME(),
               existing_nullable=True)
        batch_op.drop_column('owner_id')

    # ### end Alembic commands ###
