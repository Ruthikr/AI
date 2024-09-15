"""Change password_hash to Text

Revision ID: 469838039a4e
Revises: 
Create Date: 2024-09-15 05:07:42.474680

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '469838039a4e'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=mysql.VARCHAR(length=128),
               type_=sa.Text(),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=sa.Text(),
               type_=mysql.VARCHAR(length=128),
               existing_nullable=False)

    # ### end Alembic commands ###
