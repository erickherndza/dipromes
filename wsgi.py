import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from app import app, db, seed_if_empty, emergency_reset


@app.before_request
def _init_db_once():
    if not getattr(app, "_db_ready", False):
        with app.app_context():
            db.create_all()
            seed_if_empty()
            emergency_reset()
        app._db_ready = True


if __name__ == "__main__":
    app.run()
