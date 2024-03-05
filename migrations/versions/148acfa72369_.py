"""empty message

Revision ID: 148acfa72369
Revises: b90a1979ba53
Create Date: 2023-12-25 21:16:20.069583

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '148acfa72369'
down_revision = 'b90a1979ba53'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subscription',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('full_name', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('date_joined', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subscription')
    # ### end Alembic commands ###