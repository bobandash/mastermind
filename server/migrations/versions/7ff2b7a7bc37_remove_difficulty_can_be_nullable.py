"""Remove: difficulty can be nullable

Revision ID: 7ff2b7a7bc37
Revises: c9634c77ca9d
Create Date: 2024-04-22 01:58:28.635455

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ff2b7a7bc37'
down_revision = 'c9634c77ca9d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('waiting_room', schema=None) as batch_op:
        batch_op.add_column(sa.Column('num_rounds', sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column('difficulty_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'difficulty', ['difficulty_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('waiting_room', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('difficulty_id')
        batch_op.drop_column('num_rounds')

    # ### end Alembic commands ###
