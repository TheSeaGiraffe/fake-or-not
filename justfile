# List all available recipes
default:
    just -l -u

# Start the application using FastAPI
run:
    uv run fastapi dev

# Start the application using uvicorn
run_uvicorn:
    uv run uvicorn app.main:app --port 8000
