# Todo API

A minimal REST API for managing a to-do list, built with FastAPI and SQLite.

## How to run locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server (from the project root, one level above app/)
uvicorn app.main:app --reload

# 3. Hit an endpoint
curl -X POST http://127.0.0.1:8000/todos -H "Content-Type: application/json" -d '{"title": "Buy milk"}'
```

Interactive API docs are available at <http://127.0.0.1:8000/docs> once the server is running.

## Running tests

```bash
pytest app/test_main.py
```
