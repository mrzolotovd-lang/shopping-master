"""Add performance indexes

Revision ID: 1a2f5e082e43
Revises: 93ec0dfff3f6
Create Date: 2026-08-07 11:42:03.989832

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1a2f5e082e43'
down_revision = '93ec0dfff3f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index('ix_items_name', 'items', ['name'])
    op.create_index('ix_shopping_list_status', 'shopping_list', ['status'])
    op.create_index('ix_users_telegram_id', 'users', ['telegram_id'])
    op.create_index('ix_items_category_id', 'items', ['category_id'])
    op.create_index('ix_operation_log_created_at', 'operation_log', ['created_at'])
    op.create_index('ix_operation_log_user_id', 'operation_log', ['user_id'])
    op.create_index('ix_shopping_list_user_status', 'shopping_list', ['user_id', 'status'])


def downgrade() -> None:
    op.drop_index('ix_shopping_list_user_status', 'shopping_list')
    op.drop_index('ix_operation_log_user_id', 'operation_log')
    op.drop_index('ix_operation_log_created_at', 'operation_log')
    op.drop_index('ix_items_category_id', 'items')
    op.drop_index('ix_users_telegram_id', 'users')
    op.drop_index('ix_shopping_list_status', 'shopping_list')
    op.drop_index('ix_items_name', 'items')
