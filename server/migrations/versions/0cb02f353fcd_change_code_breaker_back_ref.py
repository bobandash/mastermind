"""Change code_breaker back_ref

Revision ID: 0cb02f353fcd
Revises: 0f482cd5ded9
Create Date: 2024-04-18 12:30:51.277744

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0cb02f353fcd'
down_revision = '0f482cd5ded9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('round', schema=None) as batch_op:
        batch_op.add_column(sa.Column('code_breaker_id', sa.String(), nullable=False))
        batch_op.drop_constraint('round_code_breaker_fkey', type_='foreignkey')
        batch_op.create_foreign_key(None, 'user', ['code_breaker_id'], ['id'])
        batch_op.drop_column('code_breaker')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('round', schema=None) as batch_op:
        batch_op.add_column(sa.Column('code_breaker', sa.VARCHAR(), autoincrement=False, nullable=False))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.create_foreign_key('round_code_breaker_fkey', 'user', ['code_breaker'], ['id'])
        batch_op.drop_column('code_breaker_id')

    # ### end Alembic commands ###