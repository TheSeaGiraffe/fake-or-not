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

When your access token expires, you can request a new one by sending a request to the
`user/token/refresh` endpoint with your refresh token in the header. When your refresh
token expires, request another set of tokens from `/user/token`. You can also revoke the
current refresh token by hitting the `user/token/revoke` endpoint.

With your access token you're now ready to use the prediction endpoint. Send Tweet text in
a JSON object with following form:

```json
{
  "model_input": ["<tweet_text>", ...]
}
```

Below is an example:

```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzUzOTQ2NjM0fQ.H7MlFt4Ywnq737FJYD0l9WxjkmcYsF_oeYcZMS5Ulhk" \
  -H "Content-Type: application/json" \
  -d '{"model_input": ["informao que aponta que <user> mandou apagar conta de carlos bolsonaro de redes sociais por causa de hashtag <hashtag> falsa e foi negada pelo <user> entenda <url>", "os fascistas do futuro se chamaro de anti-fascistas. <user> <user> <user> <user> <user> <user> <user> <user> <url>", "usa : des policiers blancs arrtent un homme noir qui se trouve tre un agent du fbi... <hashtag> <url>"]}' \
  localhost:8000/predict/
```

You should then get an output similar to the following:

```
{"model_predictions":[{"label":"misinformation","score":0.9992982149124146},{"label":"misinformation","score":0.9977389574050903},{"label":"misinformation","score":0.9946170449256897}]}
```
