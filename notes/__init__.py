"""Flask application factory: create_app() builds an app with its own SQLite database."""
from flask import Flask

from .db import close_db, init_db
from .routes import bp


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)
    app.config.update(DATABASE="notes.sqlite3")
    if config:
        app.config.update(config)
    app.teardown_appcontext(close_db)
    app.register_blueprint(bp, url_prefix="/api")
    with app.app_context():
        init_db()
    return app
