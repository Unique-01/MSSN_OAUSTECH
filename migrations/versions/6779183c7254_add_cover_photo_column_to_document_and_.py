"""Add cover photo column to document and document category

Revision ID: 6779183c7254
Revises: cccbc8bd6d72
Create Date: 2024-04-23 15:12:50.790772

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6779183c7254'
down_revision = 'cccbc8bd6d72'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('document', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cover_photo', sa.String(), nullable=True))

    with op.batch_alter_table('document_category', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cover_photo', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('document_category', schema=None) as batch_op:
        batch_op.drop_column('cover_photo')

    with op.batch_alter_table('document', schema=None) as batch_op:
        batch_op.drop_column('cover_photo')

    # ### end Alembic commands ###
