# Misinformation detection API

This is a simple API that provides predictions on whether a given Tweet contains
misinformation. It uses a BERT model fine-tuned on the text portion of the MuMiN dataset.

## Installation and Setup

Make sure you have the following prerequisites installed:

- `docker`
- `uv`
- `just` (optional)

Afterwards, clone the repo then install all project dependencies by running

```bash
uv sync
```

then create an `.env` file using the `.env.example` as a template. Once that's done spin
up a database container instance with

```bash
docker compose up -d
```

and then apply all database migrations by running one of the following commands

```bash
# If just has been installed
just migrate_up

# If just has not been installed
uv run alembic upgrade head
```

Finally, start the API with

```bash
# If just has been installed
just run_uvicorn

# If just has not been installed
uv run uvicorn app.main:app --port 8000
```

## Basic Usage

Register a user using the `/user/register` endpoint:

```bash
curl -H "Content-Type: application/json" \
  -d '{"email": "sb@homestarrunner.com", "name": "Strong Bad", "password": "123456"}' \
  localhost:8000/user/register
```

You should receive a response containing your ID, email, and name. You can now get an
access and refresh token from the `/user/token` endpoint. Since FastAPI adheres to OAuth2
you'll have to send your credentials through form fields:

```bash
curl -d "username=sb@homestarrunner.com&password=123456" localhost:8000/user/token
```

Note that for this API you should use your email rather than your name. If everything went
well you should receive both an access token and a refresh token. With your access token,
you can use protected endpoints such as `/user/me`. Assuming that you have the access
token `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzUyOTk3OTU0fQ.H9TZhGsVH0Q2K5Ftrw76mORdrJ8tX2m-IfVtyn7p9WM`
you can hit a protected endpoint in the following manner:

```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzUyOTk3OTU0fQ.H9TZhGsVH0Q2K5Ftrw76mORdrJ8tX2m-IfVtyn7p9WM" localhost:8000/user/me
```

When your access token expires, you can request a new one using your refresh token in a
way that's identical to hitting the `/user/token` endpoint. The only difference is that
the access token is replaced with the refresh token and the target endpoint is
`/user/refresh`. When your refresh token expires, request another set of tokens from
`/user/token`.
