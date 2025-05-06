#!/bin/sh

# Wait for PostgreSQL
# until psycopg2 -c "SELECT 1" -h postgres -U postgres -d fast_blog 2>/dev/null; do
#     echo "Waiting for PostgreSQL..."
#     sleep 2
# done

# Apply migrations
alembic upgrade head

# Start FastAPI
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
