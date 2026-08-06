"""Add performance indexes

Revision ID: 7345fe5efbf4
Revises: c501e33272e8
Create Date: 2026-08-06

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '7345fe5efbf4'
down_revision = 'c501e33272e8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Index for item name lookups (NLP search)
    op.create_index('ix_items_name', 'items', ['name'])
    
    # Index for shopping list filtering
    op.create_index('ix_shopping_list_status', 'shopping_list', ['status'])
    
    # Index for user lookups by Telegram ID
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'])
    
    # Index for category lookups
    op.create_index('ix_items_category_id', 'items', ['category_id'])
    
    # Index for operation log queries
    op.create_index('ix_operation_log_created_at', 'operation_log', ['created_at'])
    op.create_index('ix_operation_log_user_id', 'operation_log', ['user_id'])
    
    # Composite index for shopping list by user
    op.create_index('ix_shopping_list_user_status', 'shopping_list', ['user_id', 'status'])


def downgrade() -> None:
    op.drop_index('ix_shopping_list_user_status', 'shopping_list')
    op.drop_index('ix_operation_log_user_id', 'operation_log')
    op.drop_index('ix_operation_log_created_at', 'operation_log')
    op.drop_index('ix_items_category_id', 'items')
    op.drop_index('ix_users_telegram_id', 'users')
    op.drop_index('ix_shopping_list_status', 'shopping_list')
    op.drop_index('ix_items_name', 'items')
