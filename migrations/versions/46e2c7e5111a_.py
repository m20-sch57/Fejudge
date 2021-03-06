"""empty message

Revision ID: 46e2c7e5111a
Revises: a1baa3fd4074
Create Date: 2020-08-10 19:58:30.499530

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '46e2c7e5111a'
down_revision = 'a1baa3fd4074'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('problem', 'max_score')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('problem', sa.Column('max_score', sa.INTEGER(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
