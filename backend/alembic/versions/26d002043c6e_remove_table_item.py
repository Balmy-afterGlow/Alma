"""remove table item

Revision ID: 26d002043c6e
Revises: a47f69e6fea8
Create Date: 2025-06-22 20:43:38.701077

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '26d002043c6e'
down_revision = 'a47f69e6fea8'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tool',
    sa.Column('tool_id', sa.Uuid(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('parameters', sa.JSON(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('implementation', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('tool_id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('conversation',
    sa.Column('conversation_id', sa.Uuid(), nullable=False),
    sa.Column('title', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('conversation_id')
    )
    op.create_index(op.f('ix_conversation_user_id'), 'conversation', ['user_id'], unique=False)
    op.create_table('llmconfig',
    sa.Column('llm_id', sa.Uuid(), nullable=False),
    sa.Column('provider', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('api_key_encrypted', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('llm_id')
    )
    op.create_table('model',
    sa.Column('model_id', sa.Uuid(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('base_url', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('llm_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['llm_id'], ['llmconfig.llm_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('model_id')
    )
    op.create_table('agent',
    sa.Column('agent_id', sa.Uuid(), nullable=False),
    sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('instruction', sa.Text(), nullable=False),
    sa.Column('team', sa.JSON(), nullable=True),
    sa.Column('is_system_agent', sa.Boolean(), nullable=False),
    sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('model_id', sa.Uuid(), nullable=True),
    sa.Column('user_id', sa.Uuid(), nullable=True),
    sa.ForeignKeyConstraint(['model_id'], ['model.model_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('agent_id')
    )
    op.create_table('agenttools',
    sa.Column('agent_id', sa.Uuid(), nullable=False),
    sa.Column('tool_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['agent_id'], ['agent.agent_id'], ),
    sa.ForeignKeyConstraint(['tool_id'], ['tool.tool_id'], ),
    sa.PrimaryKeyConstraint('agent_id', 'tool_id')
    )
    op.create_table('message',
    sa.Column('message_id', sa.Uuid(), nullable=False),
    sa.Column('role', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.Column('model_metadata', sa.JSON(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=False),
    sa.Column('is_deleted', sa.Boolean(), nullable=False),
    sa.Column('conversation_id', sa.Uuid(), nullable=False),
    sa.Column('agent_id', sa.Uuid(), nullable=False),
    sa.ForeignKeyConstraint(['agent_id'], ['agent.agent_id'], ),
    sa.ForeignKeyConstraint(['conversation_id'], ['conversation.conversation_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('message_id')
    )
    op.create_index(op.f('ix_message_conversation_id'), 'message', ['conversation_id'], unique=False)
    op.drop_table('item')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('item',
    sa.Column('id', sa.UUID(), autoincrement=False, nullable=False),
    sa.Column('title', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
    sa.Column('description', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('owner_id', sa.UUID(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['owner_id'], ['user.user_id'], name='item_owner_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name='item_pkey')
    )
    op.drop_index(op.f('ix_message_conversation_id'), table_name='message')
    op.drop_table('message')
    op.drop_table('agenttools')
    op.drop_table('agent')
    op.drop_table('model')
    op.drop_table('llmconfig')
    op.drop_index(op.f('ix_conversation_user_id'), table_name='conversation')
    op.drop_table('conversation')
    op.drop_table('tool')
    # ### end Alembic commands ###