"""Change: waiting room code data type

Revision ID: 5f40cf38df2f
Revises: 0ef9c2dee84b
Create Date: 2024-04-21 17:49:26.057383

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f40cf38df2f'
down_revision = '0ef9c2dee84b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('waiting_room', schema=None) as batch_op:
        batch_op.alter_column('code',
               existing_type=sa.INTEGER(),
               type_=sa.String(length=6),
               existing_nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('waiting_room', schema=None) as batch_op:
        batch_op.alter_column('code',
               existing_type=sa.String(length=6),
               type_=sa.INTEGER(),
               existing_nullable=True)

    # ### end Alembic commands ###
