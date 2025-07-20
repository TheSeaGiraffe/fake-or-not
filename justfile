set dotenv-load

# List all available recipes
default:
    just -l -u

# Start the application using FastAPI
run:
    uv run fastapi dev

# Start the application using uvicorn
run_uvicorn:
    uv run uvicorn app.main:app --port 8000

# Connect to DB
db:
    psql "postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@$POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"

# Create a new migration
migrate_create +args:
    uv run alembic revision --autogenerate -m '{{args}}'

# Run all migrations up to latest
migrate_up:
    uv run alembic upgrade head

# Revert migration to previous version
migrate_down_one:
    uv run alembic downgrade -1
