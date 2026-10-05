# Flask Notes API

A small REST API for notes built with **Flask** and the standard-library **sqlite3** module, to practise the
Flask way of structuring an app.

## Features
- Application factory (`create_app`) and a **Blueprint** for the routes
- One SQLite connection per request (`flask.g`), closed on teardown
- CRUD: `POST /api/notes`, `GET /api/notes`, `GET /api/notes/<id>`, `PATCH /api/notes/<id>`, `DELETE /api/notes/<id>`
- Search (`?q=`) over title and body, filter by tag (`?tag=`), tags normalised to lowercase
- Parameterised SQL queries (no string formatting of user input), JSON error responses
- Tests with Flask's test client and a temporary database per test

## Run
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
flask --app "notes:create_app()" run --debug
```

## Test
```bash
pytest -q
```

## Next steps
- SQLAlchemy models and migrations
- Pagination
- JWT authentication
