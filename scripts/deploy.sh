#!/bin/bash
# Quick deployment script for Shopping Master Bot
# Usage: ./scripts/deploy.sh <DATABASE_URL>

set -e

DATABASE_URL="${1:-$DATABASE_URL}"

if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not provided"
    echo "Usage: $0 <DATABASE_URL>"
    echo "   or: export DATABASE_URL='...' && $0"
    exit 1
fi

echo "🚀 Shopping Master Deployment"
echo "=============================="
echo ""

# Check database URL (mask credentials in output)
mask_url() {
    local url="$1"
    echo "$url" | sed -E 's|(postgresql://)[^:]+:[^@]+@|\1***:***@|g'
}

echo "📊 Database: $(mask_url "$DATABASE_URL")"
if [[ ! $DATABASE_URL =~ ^postgresql:// ]]; then
    echo "❌ DATABASE_URL must start with postgresql://"
    exit 1
fi

# Test database connection
echo ""
echo "🔗 Testing database connection..."
if command -v psql &> /dev/null; then
    if PGPASSWORD=$(echo $DATABASE_URL | cut -d':' -f3 | cut -d'@' -f1) psql -h $(echo $DATABASE_URL | cut -d'@' -f2 | cut -d'/' -f1 | cut -d':' -f1) -U $(echo $DATABASE_URL | cut -d':' -f3 | cut -d'@' -f1) -d $(echo $DATABASE_URL | cut -d'/' -f4) -c "SELECT 1" &> /dev/null; then
        echo "✅ Database connection successful"
    else
        echo "⚠️  Could not test connection with psql (continuing anyway)"
    fi
else
    echo "⚠️  psql not found, skipping connection test"
fi

# Run migrations
echo ""
echo "📦 Running database migrations..."
export DATABASE_URL
alembic upgrade head

if [ $? -eq 0 ]; then
    echo "✅ Migrations applied successfully"
else
    echo "❌ Migration failed"
    exit 1
fi

# Check current revision
echo ""
echo "📋 Current migration revision:"
alembic current

# Verify tables
echo ""
echo "🔍 Verifying database schema..."
python3 -c "
import os
from sqlalchemy import create_engine, text

db_url = os.getenv('DATABASE_URL')
engine = create_engine(db_url)

with engine.connect() as conn:
    result = conn.execute(text(\"\"\"
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    \"\"\"))
    tables = [row[0] for row in result]
    
print(f'Found {len(tables)} tables:')
for table in tables:
    print(f'  ✓ {table}')
"

echo ""
echo "✅ Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "  1. Set TELEGRAM_BOT_TOKEN environment variable"
echo "  2. Run: python -m src.bot"
echo "  3. Test bot in Telegram with /start"
