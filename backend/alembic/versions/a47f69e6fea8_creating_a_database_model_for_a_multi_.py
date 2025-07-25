"""Creating a database model for a multi-agent platform

Revision ID: a47f69e6fea8
Revises: 
Create Date: 2025-06-22 20:30:28.460147

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = 'a47f69e6fea8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('nickname', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column('email', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('hashed_password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('timezone', sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
    sa.Column('language', sqlmodel.sql.sqltypes.AutoString(length=10), nullable=False),
    sa.Column('preferences', sa.JSON(), nullable=True),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_table('item',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
    sa.Column('description', sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
    sa.Column('owner_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['user.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('item')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # ### end Alembic commands ###